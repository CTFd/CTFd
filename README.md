![](https://raw.githubusercontent.com/isislab/CTFd/master/CTFd/static/original/img/logo.png)
====

CTFd is a CTF in a can. Easily modifiable and has everything you need to run a jeopardy style CTF.

# Installation: 
 1. `./prepare.sh` to install dependencies using apt.
 2. Modify [CTFd/config.py](https://github.com/isislab/CTFd/blob/master/CTFd/config.py) to your liking.
 3. Use `python serve.py` in a terminal to drop into debug mode.
 4. [Here](https://github.com/isislab/CTFd/wiki/Deployment) are some deployment options

# Creating a quick docker based database:
If you just want to try CTFd with mysql and don't want to deal with setting up a database, you can use docker for it!
 1. Install docker via `apt-get install docker.io` or get it via the official installer script (recommended)
 2. Execute the follwing command to create a mysql container:
    sudo docker run \
        -d \
        --net=host \
        --name ctfd-data \
        -v $PWD/ctfd-data:/var/lib/mysql \
        -e MYSQL_ROOT_PASSWORD=changeme \
        mysql:latest
    
    This will instaniate the mysql container with persistent storage in the folder $PWD/ctfd-data.
 3. Edit the config file `CTFd/config.py` accordingly (Use mysql, set to localhost and set the root password for mysql)
    e.g.: SQLALCHEMY_DATABASE_URI = 'mysql://root:changeme@localhost/ctfd-data'
 4. Connect to the container and create a db called `ctfd-data`
 5. Run the webservice with gunicorn
# Live Demo:
[http://demo.ctfd.io/](http://demo.ctfd.io/)

Logo by [Laura Barbera](http://www.laurabb.com/)

Theme by [Christopher Thompson](https://github.com/breadchris)
