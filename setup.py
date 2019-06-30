import os
import re

from setuptools import find_packages, setup


# Do not try to import the package to get its version.
_version_file = open(os.path.join(os.path.dirname(__file__), 'pyhound', 'version.py'))
VERSION = re.compile(r"^VERSION = '(.*?)'", re.S).match(_version_file.read()).group(1)


def read(filename):
    with open(filename) as fp:
        return fp.read()


setup(
    name="pyhound",
    version=VERSION,
    author="Polyconseil",
    author_email="opensource+pyhound@polyconseil.fr",
    description="A command-line client for the Hound source code search engine.",
    keywords="hound client source code search",
    url="",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyhound = pyhound.cli:main',
        ],
    },
    include_package_data=True,
    long_description=read('README.rst'),
    install_requires=[
        'requests<3.0',
    ],
    tests_require=[l for l in read('requirements_dev.txt').splitlines() if not l.startswith(('-', '#'))],
    test_suite='tests',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Topic :: Software Development",
    ],
)
