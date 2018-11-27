![](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/logo.png?raw=true)
====

[![Build Status](https://travis-ci.org/CTFd/CTFd.svg?branch=master)](https://travis-ci.org/CTFd/CTFd)
[![CTFd Slack](https://slack.ctfd.io/badge.svg)](https://slack.ctfd.io/)

## What is CTFd?
CTFd is a Capture The Flag framework focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

![CTFd is a CTF in a can.](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/scoreboard.png?raw=true)

## Features
 * Create your own challenges, categories, hints, and flags from the Admin Interface
    * Dynamic Scoring Challenges
    * Unlockable challenge support
    * Challenge plugin architecture to create your own custom challenges
    * Static & Regex based flags
        * Custom flag plugins
    * Unlockable hints
    * File uploads to the server or an Amazon S3-compatible backend
    * Limit challenge attempts & hide challenges
    * Automatic bruteforce protection
* Individual and Team based competitions
    * Have users play on their own or form teams to play together
 * Scoreboard with automatic tie resolution
    * Hide Scores from the public
    * Freeze Scores at a specific time
 * Scoregraphs comparing the top 10 teams and team progress graphs
 * Markdown content management system
 * SMTP + Mailgun email support
    * Email confirmation support
    * Forgot password support
 * Automatic competition starting and ending
 * Team management, hiding, and banning
 * Customize everything using the [plugin](https://github.com/CTFd/CTFd/wiki/Plugins) and [theme](https://github.com/CTFd/CTFd/tree/master/CTFd/themes) interfaces
 * Importing and Exporting of CTF data for archival
 * And a lot more...

## Install
  1. Install dependencies: `pip install -r requirements.txt`
       1. You can also use the `prepare.sh` script to install system dependencies using apt.
  2. Modify [CTFd/config.py](https://github.com/CTFd/CTFd/blob/master/CTFd/config.py) to your liking.
  3. Use `flask run` in a terminal to drop into debug mode.

You can use the auto-generated Docker images with the following command:

`docker run -p 8000:8000 -it ctfd/ctfd`

Or you can use Docker Compose with the following command from the source repository:

`docker-compose up`

Check out the [wiki](https://github.com/CTFd/CTFd/wiki) for [deployment options](https://github.com/CTFd/CTFd/wiki/Basic-Deployment) and the [Getting Started](https://github.com/CTFd/CTFd/wiki/Getting-Started) guide

## Live Demo
https://demo.ctfd.io/

## Support
To get basic support, you can join the [CTFd Slack Community](https://slack.ctfd.io/): [![CTFd Slack](https://slack.ctfd.io/badge.svg)](https://slack.ctfd.io/)

If you prefer commercial support or have a special project, feel free to [contact us](https://ctfd.io/contact/).

## Managed Hosting
Looking to use CTFd but don't want to deal with managing infrastructure? Check out [the CTFd website](https://ctfd.io/) for managed CTFd deployments.

## MajorLeagueCyber
CTFd is heavily integrated with [MajorLeagueCyber](https://majorleaguecyber.org/). MajorLeagueCyber (MLC) is a CTF stats tracker that provides event scheduling, team tracking, and single sign on for events. 

By registering your CTF event with MajorLeagueCyber users can automatically login, track their individual and team scores, submit writeups, and get notifications of important events. 

To integrate with MajorLeagueCyber, simply register an account, create an event, and install the client ID and client secret in the relevant portion in `CTFd/config.py` or in the admin panel:

```python
OAUTH_CLIENT_ID = None
OAUTH_CLIENT_SECRET = None
```

## Credits
 * Logo by [Laura Barbera](http://www.laurabb.com/)
 * Theme by [Christopher Thompson](https://github.com/breadchris)
