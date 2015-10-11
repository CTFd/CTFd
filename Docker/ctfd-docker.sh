#!/bin/bash
DOCKER_IMAGE="isislabs/ctfd"
PORT=8080
VOLUMEMNT="/opt/ctfd"
CONTAINERNAME="ctfd"

if [ "$1" == "build" ]; then
	docker build --tag="$DOCKER_IMAGE" .
elif [ "$1" == "prepare" ]; then
	git clone https://github.com/isislab/CTFd.git $VOLUMEMNT
	docker run -it --rm -v $VOLUMEMNT:/opt/ctfd:Z -p $PORT:8000 $DOCKER_IMAGE prepare
elif [ "$1" == "shell" ]; then
	docker run --rm -it -v $VOLUMEMNT:/opt/ctfd:Z -p $PORT:8000 $DOCKER_IMAGE 
elif [ "$1" == "run" ]; then
	docker run -d -v $VOLUMEMNT:/opt/ctfd:Z -p $PORT:8000 --name=$CONTAINERNAME $DOCKER_IMAGE run
fi
