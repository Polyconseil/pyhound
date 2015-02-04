import os
import re

from setuptools import find_packages, setup


# Do not try to import the package to get its version.
_version_file = open(os.path.join(os.path.dirname(__file__), 'pyhound', 'version.py'))
VERSION = re.compile(r"^VERSION = '(.*?)'", re.S).match(_version_file.read()).group(1)


def load_requirements(filename):
    path = os.path.join(filename)
    with open(path) as fp:
        return [line for line in fp.read().split("\n") if line and not line.startswith(("-r", "#"))]

setup(
    name="pyhound",
    version=VERSION,
    author="Polyconseil",
    author_email="opensource+pyhound@polyconseil.fr",
    description=("A command-line client for the Hound source code search engine."),
    keywords="hound client source code search",
    url="",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyhound = pyhound.cli:main',
        ],
    },
    include_package_data=True,
    long_description=open('README.rst').read(),
    install_requires=load_requirements('requirements.txt'),
    tests_require=load_requirements('requirements_dev.txt'),
    extras_require={
        ':python_version=="2.6"': ['argparse'],
    },
    test_suite='tests',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        "Topic :: Software Development",
    ],
)
