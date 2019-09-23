from setuptools import find_packages, setup

def read(filename):
    with open(filename) as fp:
        return fp.read()


setup(
    name="pyhound",
    version='1.0.0',
    author="Polyconseil",
    author_email="opensource+pyhound@polyconseil.fr",
    description="A command-line client for the Hound source code search engine.",
    keywords="hound client source code search",
    url="https://github.com/Polyconseil/pyhound",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyhound = pyhound.cli:main',
        ],
    },
    include_package_data=True,
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
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
