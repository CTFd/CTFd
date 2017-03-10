![](https://raw.githubusercontent.com/isislab/CTFd/master/CTFd/static/original/img/logo.png)
====

[![Build Status](https://travis-ci.org/isislab/CTFd.svg?branch=master)](https://travis-ci.org/isislab/CTFd)
[![CTFd Slack](https://slack.ctfd.io/badge.svg)](https://slack.ctfd.io/)

CTFd is a CTF in a can. Easily modifiable and has everything you need to run a jeopardy style CTF.

Debian install:

1. Clone the CTFd repository: `git clone https://github.com/isislab/CTFd.git ctfd`
2. Then `cd ctfd`
3. Install general requirements: `sudo apt-get install build-essential python-dev python-pip libffi-dev -y`
4. Install python requirements: `pip install -r requirements.txt`
5. Modify [`CTFd/config.py`](https://github.com/isislab/CTFd/blob/master/CTFd/config.py) to your liking.
6. Use `python serve.py` in a terminal to drop into debug mode.
7. [Here](http://flask.pocoo.org/docs/0.10/deploying/) are some Flask deployment options.
8. [Here](https://github.com/isislab/CTFd/wiki/Deployment) are some deployment options for CTFd.

ArchLinux install:

1. Clone the CTFd repository: `git clone https://github.com/isislab/CTFd.git ctfd`
2. Then `cd ctfd`
3. Install general requirements: `sudo pacman -S --needed --noconfirm base-devel python-pip libffi`
1. Install python requirements: `pip2 install --user -r requirements.txt`
5. Modify [`CTFd/config.py`](https://github.com/isislab/CTFd/blob/master/CTFd/config.py) to your liking.
6. Use `python2 serve.py` in a terminal to drop into debug mode.
7. [Here](http://flask.pocoo.org/docs/0.10/deploying/) are some Flask deployment options.
8. [Here](https://github.com/isislab/CTFd/wiki/Deployment) are some deployment options for CTFd.

Live Demo:
https://demo.ctfd.io/

Reverse Engineering Module:
https://reversing.ctfd.io/

Logo by [Laura Barbera](http://www.laurabb.com/)

Theme by [Christopher Thompson](https://github.com/breadchris)
