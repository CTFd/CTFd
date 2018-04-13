@echo off
pause>press any key to download&install python
explorer https://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi
pause
pip install win_inet_pton
pip install -r requirements.txt
