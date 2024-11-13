#!/bin/bash
# Script to pin Python requirements in a Docker container
ROOTDIR=`pwd -P`
docker run \
    --rm \
    --entrypoint bash \
    -v $ROOTDIR:/mnt/CTFd \
    -e CUSTOM_COMPILE_COMMAND='./scripts/pip-compile.sh' \
    -it python:3.11-slim-bookworm \
    -c 'cd /mnt/CTFd && pip install pip-tools==7.4.1 && pip-compile'
