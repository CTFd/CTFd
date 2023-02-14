# Practical Security Framework

## What is this?

A final project for [COMS 6156] Topics in Software Engineering. This framework is aimed to replace the practical component of Columbia University's Security I course. It aims to bring Jeopardy-style CTF exercises to the classroom.

## Contents

This framework is built on top of [CTFd](https://github.com/CTFd/CTFd), and was added to and customized for the needs of a classroom setting.

`CTFd` holds all of the source code for the web-framework itself

`challenges` holds a collection of CTF challenges developed specifically for this project

## Installation

It is highly recommended to install this framework on a GCloud instance if used for a class or event.

To run the framework you need to:

1. Ensure that [Docker & Docker Compose](https://docs.docker.com/get-docker/) are installed
2. Run `docker-compose build` in the root directory of this repository
3. Run `docker-compose up` in the root of this repository
4. The framework should be up and running on `port 8000`

### GCloud Installation

1. Create a new project on GCloud and create a compute engine
2. Add you SSH key to the virtual instance
3. Open up all (or necessary) ports on the instance
4. SSH in and clone the repository
5. Run the above commands

### Usage

If this is your first time creating an instance of the framework, it will ask you to go through a setup procedure in order to get it up and running.

The all users will then be able to login/register in order to access the following pages
- Users: see all registered users, if set to open by admin
- Scoreboard: see all scores, if set to open by admin
- Challenges: see all available challenges
- Notifications: see all notifications sent by admin
- Profile: see your own statistics
- Settings: edit profile information

Admins will also have access to an Admin Panel where they will be able to do the following:

- Statistics: see and download summary of all statistics for all challenges, useful for grading as score distribution can be downloaded
- Notifications: Send notification to all users
- Pages: Access your pages. Both Markdown and HTML are supported.
  - All Pages: View and edit your created pages
  - New Page: Create a new page that will be displayed in the top navigation bar
- Users: Access user database
  - See profiles and statistics
  - Edit user profiles
  - Reset passwords
  - Change Roles: currently only admin and non-admin
- Scoreboard: See scoreboard, access student accounts
- Challenges: Create and push challenges
  - Admin is able to create a new challenge, write description (HTML & Markdown supported), add flag, add hints, add category, enter point value, and upload all necessary files
  - Note that currently the challenges need to be deployed separately, please see [Challenges](#challenges) for how to deploy.
- Submissions: see all submitted flags

If the server is taken down, and then restarted all of the infomration will still be there, as it is stored separately in the `.data` directory. If you would like to start from a clean slate, please delete the `.data` directory and restart the server.

### Data

All of your data is stored in a generated `.data` repository. It includes all account information, changes to the framework (such as setup, challenges, pages, etc.)

## Challenges

The collection of challenges created for this framework can be found in `challenges`. There are four categories:

- `basic`: challenges that will get the students set up and on a level starting ground
- `crypto`: cryptography-related challenges
- `pwn`: memory safety-related challenges
- `web`: web-related challenges

All challeges have a `DESCRIPTION.md` file that will describe the challenge, as well as a solution and a flag that is associated with it.

Some challenges may require a server-instance to be spun up to be accessible. To do so, please simply run:

1. `docker-compose build`
2. `docker-compose up`

And the challenge will spin up on the port that is described in `docker-compose.yml` and in `DESCRIPTION.md`

## Future Work

1. Development of more challenges that will complete the Security I curriculum's practical requirements
2. Development of feature to allow students to upload their code and writeup directly on the website
3. Tying in [ctfcli](https://github.com/CTFd/ctfcli) for automated challenge publishing onto the website.
4. Implementation of dynamic flags tied to students, that will allow anti-cheating. (System where if two students submit the same flag, you know they cheated.)
