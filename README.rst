**pyhound** is a command line client for the `Hound`_ source code
search engine. It connects to a Hound server. Here is an absolutely
not fabricated example::

    $ pyhound frobulate
    devguide:tools/frob.rst:433:if you really have to frobulate things, be sure to
    footils:tests/test_frob.py:378:    eventlog_api.log_business(obj, 'frobulated', obj)
    frobulator:src/frobulator/handler.py:47:    error="Could not frobulate event.",

.. _Hound: https://github.com/hound-search/Hound


Requirements
============

**pyhound** needs Python 3. It supports versions >= 3.5.


Installation
============

**pyhound** needs a Hound server. See Hound documentation for further
details. The steps below assume that you have a Hound server listening
(for example on ``http://localhost:6080``).

To install **pyhound**, use ``pip``::

    pip install pyhound


Features
========

**pyhound** aims to output search results in the manner of ``grep``
and hence implements some (but definitely not all) of its options.

The main feature of **pyhound** is its ``--help`` argument::

    usage: pyhound [-h] [--version] [--endpoint URL] [--repos REPOSITORY_LIST]
                   [--exclude-repos REPOSITORY_LIST] [--path FILE_PATH_PATTERN]
                   [-A NUM] [-B NUM] [-C NUM] [--color [WHEN]] [-i] [-n]
                   [--line-max-length LINE_MAX_LENGTH]
                   PATTERN
    
    A command-line client for Hound.
    
    positional arguments:
      PATTERN               The regular expression to search.
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --endpoint URL        Host and port of the Hound server. You may also set a
                            HOUND_ENDPOINT environment variable. Default:
                            http://localhost:6080/
      --repos REPOSITORY_LIST
                            A comma-separated list of repositories to search in.
                            Default: all.
      --exclude-repos REPOSITORY_LIST
                            A comma-separated list of repositories to exclude.
      --path FILE_PATH_PATTERN
                            A pattern to match against the path of candidate
                            files.
      -A NUM, --after-context NUM
                            Print NUM lines of trailing context after matching
                            lines. Cannot be used with -C.
      -B NUM, --before-context NUM
                            Print NUM lines of leading context before matching
                            lines. Cannot be used with -C.
      -C NUM, --context NUM
                            Print NUM lines of output context. Cannot be used with
                            -A or -B.
      --color [WHEN], --colour [WHEN]
                            Surround the matched (non-empty) strings, file names,
                            line numbers and separators (for fields and groups of
                            context lines) with escape sequences to display them
                            in color on the terminal. WHEN may be "never",
                            "always" or "auto".
      -i, --ignore-case     Ignore case distinctions in both the PATTERN and the
                            input files.
      -n, --line-number     Prefix each line of output with the 1-based line
                            number within its input file.
      --line-max-length LINE_MAX_LENGTH
                            If given, don't show matching lines if they are longer
                            than requested.


Limitations
===========

**pyhound** currently tries to retrieve all search results in a single
request to the Hound server. The server may return an error if there
are too many results (currently: more than 5000) and **pyhound** will
kindly display this error. The Hound web user interface has the same
limitation and fails in a similar way (although it at least shows the
first 20 results).

A future version of **pyhound** may handle this case and make multiple
requests to the Hound server. On the other hand, the usefulness of
displaying more than 5000 search results seems questionable.


Alternatives
============

Apart from the web user interface, Hound comes with a command-line
client. But it does not provide a ``grep``-like output. There is a
comment in the source code that suggests that it may appear someday,
but the comment has been there for 4 years (as of July 2019), so it's
unlikely to happen anytime soon.

Doug Hellmann has released Beagle (also in Python) in February 2018.
It seems to concentrate on supporting multiple (many!) output formats,
including a ``grep``-like one. I did not test it.


The name
========

I must apologize. It's the first time I write a Python package that
starts with "py". I thought I could resist a few more years. How naive
of me...


Credits, contributions and license
==================================

Well, first things first: thanks to the developers of Hound. :)

**pyhound** is maintained by developpers at `Polyconseil`_. It is
hosted on GitHub at https://github.com/polyconseil/pyhound/.
Suggestions and patches are welcome.

Continuous tests are run on `Travis CI <https://travis-ci.org>`_.
Current status: |travis-ci-status|_

.. |travis-ci-status| image:: https://travis-ci.org/Polyconseil/pyhound.svg?branch=master

.. _travis-ci-status: https://travis-ci.org/Polyconseil/pyhound

**pyhound** is licensed under the 3-clause BSD license, a copy of
which is included in the source.

.. _Polyconseil: http://www.polyconseil.fr
