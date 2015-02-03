from __future__ import unicode_literals

import argparse
import os
import sys

from pyhound.hound import Client
from pyhound.version import VERSION


PY2 = sys.version[0] == '2'

DEFAULT_ENDPOINT = 'http://localhost:6080/'


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="pyhound",
        description="A command-line client for Hound.")
    parser.add_argument('--version', action='version', version='%%(prog)s %s' % VERSION)

    # Hound-specific options
    default_endpoint = os.environ.get('HOUND_ENDPOINT', DEFAULT_ENDPOINT)
    parser.add_argument(
        '--endpoint', metavar='URL', action='store', default=default_endpoint,
        help="Host and port of the Hound server. You may also set a HOUND_ENDPOINT "
             "environment variable. Default: %s" % default_endpoint)

    parser.add_argument(
        '--repos', metavar='REPOSITORY_LIST', action='store', default='*',
        help="A comma-separated list of repositories to search in. Default: all.")

    parser.add_argument(
        '--exclude-repos', metavar='REPOSITORY_LIST', action='store', default=None,
        help="A comma-separated list of repositories to exclude.")

    parser.add_argument(
        '--path', metavar='FILE_PATH_PATTERN', action='store', dest='path_pattern', default=None,
        help="A pattern to match against the path of candidate files.")

    # Help text of grep-like options have been adapted from the grep
    # manual.

    # Grep-like options: context (-A, -B, -C)
    parser.add_argument(
        '-A', '--after-context', metavar='NUM', action='store', type=int,
        help="Print NUM lines of trailing context after matching lines. Cannot be used with -C.")
    parser.add_argument(
        '-B', '--before-context', metavar='NUM', action='store', type=int,
        help="Print NUM lines of leading context before matching lines. Cannot be used with -C.")
    parser.add_argument(
        '-C', '--context', metavar='NUM', action='store', type=int,
        help="Print NUM lines of output context. Cannot be used with -A or -B.")

    # Grep-like options: colors (--color)
    parser.add_argument(
        '--color', '--colour', metavar='WHEN', nargs='?', action='store',
        choices=('never', 'always', 'auto'),
        # The default value is stored if '--color' is not used at all.
        # If '--color' is used without any argument, we get None. See 'main()'.
        default='never',
        help='Surround the matched (non-empty) strings, file names, line numbers and separators '
             '(for fields and groups of context lines) with escape sequences to display them in '
             'color on the terminal. WHEN may be "never", "always" or "auto".')

    # Grep-like options: case sensitivity (-I)
    parser.add_argument(
        '-i', '--ignore-case', action='store_true',
        help="Ignore case distinctions in both the PATTERN and the input files.")

    # Grep-like options: line numbers (-n)
    parser.add_argument(
        '-n', '--line-number', action='store_true', dest='show_line_number',
        help="Prefix each line of output with the 1-based line number within its input file.")

    # Positional argument: the pattern to search.
    parser.add_argument(
        'pattern', metavar="PATTERN", action='store',
        help="The regular expression to search.")

    return parser.parse_args(args)


def get_endpoint(options):
    return options.hound_endpoint


def main():
    options = parse_args(sys.argv[1:])
    # If the user calls "--color" without any value, we get None.
    if options.color is None:
        options.color = 'auto'
    if PY2:
        # In Python 2, we get byte strings (str) from argparse. We
        # would prefer unicode objects to be in line with what we get
        # in Python 3.
        options.pattern = options.pattern.decode(sys.stdin.encoding)
        options.path_pattern = (options.path_pattern or '').decode(sys.stdin.encoding)
    c = Client(**options.__dict__)
    return c.run()


if __name__ == '__main__':
    main()
