#!/bin/sh

sudo apt-get install build-essential python-dev python-pip libffi-dev
pip install -r requirements.txt

# Requirements for SASS
sudo apt-get install ruby -y
sudo gem install sass

# Start watching for changes to SASS
mkdir log
nohup sass --watch static/sass/materialize.scss:static/css/materialize.css > log/$(/bin/date +%Y%m%d.%H%M).sass_watch.log 2>&1 &
