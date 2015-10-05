README
======

Build and Start
---------------

0. Edit './ctfd-docker.sh' variables to change default settings including port, volume location, and container/image names.
0. Run './ctfd-docker.sh build' to build the docker container
0. Run './ctfd-docker.sh prepare' to download and install pip requirements
0. Run './ctfd-docker.sh run' to start CTFd

Config
------

The CTFd config can be changed by going to the volume mount point and edit it as normal. This defaults to /opt/ctfd

Debug
-----

To debug the container or git an interactive shell at start run './ctfd-docker.sh shell'


