![](https://github.com/CoolDUp/CTFdPlus/blob/master/CTFd/themes/pzctf/static/img/logo.png?raw=true)
====
# CTFd+

## What is CTFd+?

* CTFd++ is a branch of CTFd.It's a Capture The Flag framework focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

* CTFd+ 是CTFd的一个分支，扩展了一些高级功能。这是一个集易用性和可定制性的CTF比赛平台框架。具有定制语言,插件和主题的高扩展性。

![CTFd+ is a CTF in a can.](https://github.com/CoolDUp/CTFdPlus/blob/master/CTFd/themes/pzctf/static/img/scoreboard.png?raw=true)

## Preview
* English https://ctfdplus.cooldup.com/
* 中文版 https://ctf.cooldup.com/

## Install
* ### Ubuntu
 1. cd <you_work_dir> Run `git clone https://github.com/CoolDUp/CTFdPlus.git` (`sudo apt-get install git`)
 2. Run `./uprepare.sh` to install dependencies using apt.
 3. Modify Config `vi CTFd/config.py`
 4. Run `python genkey.py` get your secret_key and save it
 5. Use `python serve.py` in a terminal to drop into debug mode.
* ### Centos
 1. cd <you_work_dir> Run `git clone https://github.com/CoolDUp/CTFdPlus.git` (`sudo yum install -y git`)
 2. Run `./cprepare.sh` to install dependencies using yum.
 3. Modify Config `vi CTFd/config.py`
 4. Run `python genkey.py` get your secret_key and save it
 5. Use `python serve.py` in a terminal to drop into debug mode.
* ### Windows
 1. Download https://github.com/CoolDUp/CTFdPlus/archive/master.zip & cd <you_work_dir>
 2. Run `./prepare.bat` to install dependencies.
 3. Modify Config [CTFd/config.py]
 4. Run `python genkey.py` get your secret_key and save it
 5. Use `python serve.py` in a terminal to drop into debug mode.
* ### Docker
    * how to install docker or docker-compose ?
    > * `docker run -p 8000:8000 -it ctfd/ctfd`
    * With docker-compose you can   
    > * `cd /home/docker` & `git clone https://github.com/CoolDUp/CTFdPlus.git`
    > * `docker-compose build`
    > * `docker-compose up -d`
* ### Solution
    * Install lamp farmework or install nginx only
    * Modify nginx config like /solution 's file
    * Install docker &  docker-compose  
    > * `cd /home/docker` & `git clone https://github.com/CoolDUp/CTFdPlus.git`
    > * `docker-compose build`
    > * `docker-compose up -d`
    > * set firewall stop default port 8000 and allow 80 port
    > * ####Visit your CTFd+ Platform !
 
## Features of CTFd
 * Create your own challenges, categories, hints, and flags from the Admin Interface
    * Static & Regex based flags
    * Users can unlock hints for free or with points
    * File uploads to the server or [Amazon S3](https://github.com/CTFd/CTFd-S3-plugin)
    * Limit challenge attempts & hide challenges
    * Automatic submission throttling
 * Scoreboard with automatic tie resolution
    * Hide Scores from the public
    * Freeze Scores at a specific time
    * [Dynamic Scoring](https://github.com/CTFd/DynamicValueChallenge)
 * Scoregraphs comparing the top 10 teams and team progress graphs
 * Markdown content management system
 * SMTP + Mailgun email support
    * Email confirmation support
    * Forgot password support
 * Automatic competition starting and ending
 * Team management & hiding
 * Customize everything using the [plugin](https://github.com/CTFd/CTFd/wiki/Plugins) and [theme](https://github.com/CTFd/CTFd/tree/master/CTFd/themes) interfaces
 * Importing and Exporting of CTF data for archival
 * And a lot more...
 
## Features of CTFd+
* Add Language Support
* Add Team-Token to Verify Flag
* Add Dynamic Flag Support (see plugins/keys/ReadMe)


## Credits
 * CTFd by [CTFd](https://ctfd.io/)
 * Logo by [Laura Barbera](http://www.laurabb.com/)
 * Theme by [Christopher Thompson](https://github.com/breadchris)
 * Theme PZCTF by [shell01] (http://shell01.cn)
