Upload C/C++ coverage report to coveralls.io
=============

[![Build Status](https://travis-ci.org/eddyxu/cpp-coveralls.png?branch=master)](https://travis-ci.org/eddyxu/cpp-coveralls)

Inspired from [z4r/python-coveralls](https://github.com/z4r/python-coveralls), it uploads the coverage report of C/C++ project to [coveralls.io](https://coveralls.io/)

# Features (0.0.6)
 * Automatically run `gcov` against coverage reports and collect the data.
 * Support any continuous integration platform and service (e.g. [Travis CI](https://travis-ci.org/) )
 * Support "out of source builds" (e.g., CMake)

# Instruction

 * Build your project with [gcov support](http://gcc.gnu.org/onlinedocs/gcc/Gcov.html)
 * Run tests
 * Run `coveralls`

## Usage:

```sh
$ coveralls -h
usage: coveralls [-h] [--gcov FILE] [-r DIR] [-e DIR|FILE] [-y FILE]
                 [-t TOKEN] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --gcov FILE           Sets the location of gcov
  -r DIR, --root DIR    Sets the root directory
  -e DIR|FILE, --exclude DIR|FILE
                        Exclude file or directory.
  -y FILE, --coveralls-yaml FILE
                        Coveralls yaml file name (default: .coveralls.yml).
  -t TOKEN, --repo_token TOKEN
                        Manually sets the repo_token of this project.
  --verbose             print verbose messages.
```

## Example `.travis.yml`

```
language: cpp
compiler:
  - gcc
before_install:
  - sudo pip install cpp-coveralls --use-mirrors
script:
  - ./configure --enable-gcov && make && make check
after_success:
  - coveralls --exclude lib --exclude tests
```
