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
3. Tying in [ctfcli](https://github.com/CTFd/ctfcli) for automated publishing onto the website.

## Demo
The demo for this project can be found [here](https://youtu.be/EvnthINztJk)