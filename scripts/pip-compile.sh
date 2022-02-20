#!/bin/bash
# Script to pin Python requirements in a Docker container
ROOTDIR=`pwd -P`
docker run \
    --rm \
    --entrypoint bash \
    -v $ROOTDIR:/mnt/CTFd \
    -e CUSTOM_COMPILE_COMMAND='./scripts/pip-compile.sh' \
    -it python:3.7 \
    -c 'cd /mnt/CTFd && pip install pip-tools==6.5.1 && pip-compile'
