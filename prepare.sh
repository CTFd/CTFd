#!/bin/sh

sudo apt-get install build-essential python-dev python-pip libffi-dev
pip install -r requirements.txt

# Requirements for SASS
sudo apt-get install ruby -y
sudo gem install sass bootstrap-sass compass
compass compile 

nohup compass watch static/sass &
