#!/bin/sh
sudo pacman -Syu
sudo pacman -Sy base-devel python python-pip libffi
pip install -r requirements.txt
