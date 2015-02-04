from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import locale
import math
import re
import sys

import requests


PY2 = sys.version[0] == '2'

DEFAULT_TIMEOUT = 5

# Warning: MATCH must have a lower value than CONTEXT
LINE_KIND_MATCH = 1
LINE_KIND_CONTEXT = 2

# See GREP_COLORS at http://www.gnu.org/software/grep/manual/html_node/Environment-Variables.html
COLOR_REPO = "\033[1m%s\033[0m"           # repo name: bold
COLOR_DELIMITER = "\033[36m%s\033[0m"     # se: cyan
COLOR_FILENAME = "\033[35m%s\033[0m"      # fn: magenta
COLOR_MATCH = "\033[1m\033[31m%s\033[0m"  # ms/mc/mt: bold red
COLOR_LINE_NUMBER = "\033[32m%s\033[0m"   # ln: green


def colorize_match(line, pattern, color):
    def colorize(re_match):
        start, end = re_match.span()
        return color % re_match.string[start:end]
    return re.subn(pattern, colorize, line)[0]


def get_lines_with_context(
        line, line_number,
        lines_before=(), lines_after=(),
        requested_before=None, requested_after=None, requested_context=None):
    """Return the given line with its line kind and its line number with
    the requested context (if any).

    This function returns an iterator. Each item is a tuple with the 3
    items: the line number, the line kind (see LINE_KIND_*) and the
    line itself.

    This implements the "-A", "-B" and "-C" options of ``grep``.
    """
    requested_before = requested_before or 0
    requested_after = requested_after or 0
    assert requested_before >= 0
    assert requested_after >= 0
    if requested_context is not None:
        assert requested_context >= 1
    if requested_before or requested_after:
        assert requested_context is None

    if requested_context is not None:
        requested_context -= 1  # Don't count the matching line.
        requested_before = int(math.ceil(requested_context / 2))
        requested_after = requested_context - requested_before
        requested_after = min(requested_after, len(lines_after))
        requested_before = requested_context - requested_after

    before = ()
    after = ()
    if requested_before and requested_before > 0:
        before = lines_before[-requested_before:]
        n_before = len(before)
    if requested_after and requested_after > 0:
        after = lines_after[:requested_after]
    for i, contextual_line in enumerate(before):
        yield line_number - n_before + i, LINE_KIND_CONTEXT, contextual_line
    yield line_number, LINE_KIND_MATCH, line
    for i, contextual_line in enumerate(after, 1):
        yield line_number + i, LINE_KIND_CONTEXT, contextual_line


def merge_lines(lines):
    """Merge lines when matching and contextual lines overlap.

    When matching and contextual lines overlap, some lines are
    duplicated. This function merges all lines so that they appear
    only once and have the right "line kind".

    FIXME: this is probably inefficient
    """
    # Sort by line number and line kind (match first).
    sorted_lines = sorted(lines, key=lambda l: (l[2], l[3]))
    seen = set()
    for repo, filename, line_number, line_kind, line in sorted_lines:
        if line_number in seen:
            continue
        seen.add(line_number)
        yield repo, filename, line_number, line_kind, line


class Client(object):

    def __init__(self,
            endpoint,
            pattern,
            repos='*',
            exclude_repos=None,
            path_pattern='',
            after_context=None, before_context=None, context=None,
            color='never',
            ignore_case=False,
            show_line_number=False,
            ):
        # Endpoints
        endpoint = endpoint.rstrip('/')
        self.endpoint_list_repos = '%s/api/v1/repos' % endpoint
        self.endpoint_search = '%s/api/v1/search' % endpoint

        self.pattern = pattern

        # Hound-related options.
        self.repos = self.get_repo_list(repos, exclude_repos)
        self.path_pattern = path_pattern

        # Grep-like options.
        assert not (before_context and context)
        assert not (after_context and context)
        self.after_context = after_context
        self.before_context = before_context
        self.context = context
        if color == 'auto':
            color = sys.stdout.isatty()
        elif color == 'always':
            color = True
        else:
            color = False
        self.color = color
        self.ignore_case = ignore_case
        self.show_line_number = show_line_number

    def get_repo_list(self, repos, exclude_repos):
        """Return a comma-separated list of repositories to look in.

        This method may call Hound API.
        """
        if not exclude_repos:
            return repos
        if repos == '*':
            response = self._call_api(self.endpoint_list_repos)
            repos = set(response.keys())
        else:
            repos = set(r.strip() for r in repos.split(','))
        exclude_repos = set(r.strip() for r in exclude_repos.split(','))
        repos = sorted(repos - exclude_repos)
        return ','.join(repos)

    def run(self):
        results = self.get_search_results()
        lines = self.get_lines(results)
        self.print_lines(lines)

    def get_search_results(self):
        """Call Hound API to perform search."""
        payload = {
            'repos': self.repos,
            'rng': '',  # range. Empty, we want all results.,
            'files': self.path_pattern,
            'i': 'true' if self.ignore_case else '',
            'q': self.pattern,
        }
        response = self._call_api(self.endpoint_search, payload)
        return response['Results']

    def _call_api(self, endpoint, payload=None):
        """Call API on Hound server and undecode JSON response.

        If any error occurs, we exit the program with an error
        message.
        """
        try:
            response = requests.get(
                endpoint,
                params=payload,
                timeout=DEFAULT_TIMEOUT,
            )
        except (requests.ConnectionError, requests.HTTPError) as exc:
            # exc.args[0] is the original exception that `requests`
            # wraps. We could probably make the output better for some
            # cases but I am not keen to guess how each exception
            # looks like.
            sys.exit("Could not connect to Hound server: %s" % exc.args[0])
        except requests.Timeout:
            sys.exit("Could not connect to Hound server: timeout.")

        try:
            json = response.json()
        except ValueError:
            sys.exit(
                "Server did not return a valid JSON response. "
                "Got this instead:\n%s" % response.text
            )

        if 'Error' in json:
            sys.exit("Hound server returned an error: %s" % json['Error'])
        return json

    def get_lines(self, results):
        for repo, result in results.items():
            for match in result['Matches']:
                lines = []
                filename = match['Filename']
                for file_match in match['Matches']:
                    lines.extend(self.get_lines_for_repo(repo, filename, file_match))
                if self.before_context or self.after_context or self.context:
                    lines = merge_lines(lines)
                for line in lines:
                    yield line

    def get_lines_for_repo(self, repo, filename, match):
        for line_number, line_kind, line in get_lines_with_context(
                match['Line'],
                match['LineNumber'],
                match['Before'],
                match['After'],
                self.before_context,
                self.after_context,
                self.context):
            yield (repo, filename, line_number, line_kind, line)

    def print_lines(self, lines):
        encoding = locale.getdefaultlocale()[1] or 'utf-8'
        for repo, filename, line_number, line_kind, line in lines:
            if self.show_line_number:
                fmt = "{repo}:{filename}{delim}{line_number}{delim}{line}"
            else:
                fmt = "{repo}:{filename}{delim}{line}"
            delim = ':' if line_kind == LINE_KIND_MATCH else '-'
            if self.color:
                repo = COLOR_REPO % repo
                filename = COLOR_FILENAME % filename
                line_number = COLOR_LINE_NUMBER % line_number
                delim = COLOR_DELIMITER % delim
                pattern_re = re.compile(self.pattern, flags=re.IGNORECASE if self.ignore_case else 0)
                line = colorize_match(line, pattern_re, COLOR_MATCH)
            out = fmt.format(
                repo=repo,
                filename=filename,
                line_number=line_number,
                delim=delim,
                line=line)
            # FIXME: "I'm getting heartburn. Tony, do something terrible."
            if PY2:
                print(out.encode(encoding))
            else:
                print(out)
