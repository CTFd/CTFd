#!/bin/bash

#Copy binary from temporary container
docker-compose up --no-start --build
docker cp $(docker ps -alq):/build .

