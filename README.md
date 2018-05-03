![](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/logo.png?raw=true)
====

[![Build Status](https://travis-ci.org/CTFd/CTFd.svg?branch=master)](https://travis-ci.org/CTFd/CTFd)
[![CTFd Slack](https://slack.ctfd.io/badge.svg)](https://slack.ctfd.io/)

## What is CTFd?
CTFd is a Capture The Flag framework focusing on ease of use and customizability. It comes with everything you need to run a CTF and it's easy to customize with plugins and themes.

![CTFd is a CTF in a can.](https://github.com/CTFd/CTFd/blob/master/CTFd/themes/core/static/img/scoreboard.png?raw=true)

## Features
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

## Install
 1. Run `./prepare.sh` to install dependencies using apt.
 2. Modify [CTFd/config.py](https://github.com/CTFd/CTFd/blob/master/CTFd/config.py) to your liking.
 3. Use `flask run` in a terminal to drop into debug mode.

Or you can use Docker with the following command:

`docker run -p 8000:8000 -it ctfd/ctfd`

 * [Here](https://github.com/CTFd/CTFd/wiki/Basic-Deployment) are some deployment options
 * You can check out the [Getting Started](https://github.com/CTFd/CTFd/wiki/Getting-Started) guide for a breakdown of some of the features you need to get started.

## Live Demo
https://demo.ctfd.io/

## Support
To get basic support, you can join the [CTFd Slack Community](https://slack.ctfd.io/): [![CTFd Slack](https://slack.ctfd.io/badge.svg)](https://slack.ctfd.io/)

If you prefer commercial support or have a special project, send us an email: [support@ctfd.io](mailto:support@ctfd.io).

## Managed Hosting
Looking to use CTFd but don't want to deal with managing infrastructure? Check out [the CTFd website](https://ctfd.io/) for managed CTFd deployments.

## HackerFire
Looking for CTF challenges to work on? [HackerFire](https://hackerfire.com/) is a learning focused CTF built using CTFd. It features a wide variety of challenges and is updated with new content frequently. It also contains custom knowledge resources to teach newcomers about the techniques used to solve a challenge.

## Credits
 * Logo by [Laura Barbera](http://www.laurabb.com/)
 * Theme by [Christopher Thompson](https://github.com/breadchris)
