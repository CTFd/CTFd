#!/bin/sh
sudo yum update
sudo yum -y install build-essential python-dev python-pip libffi-dev
pip install -r requirements.txt