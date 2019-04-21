#!/bin/bash

USERID=$(id -u)
GID=$(id -g)

cp Dockerfile.orig Dockerfile
cp docker-compose.yml.orig docker-compose.yml
echo "Choose secret:"
read -r -s secret

# Replace UID with current uid (create .bak file for macOSx portability)
sed -i  .bak "s/1001/$USERID/g" Dockerfile
# Prepare data directories for user
mkdir -p .data/CTFd/logs
mkdir -p .data/CTFd/uploads
chown $USERID:$GID  .data/CTFd/logs
chown $USERID:$GID  .data/CTFd/uploads

sed  -i .bak    "10i\\
  \ \ \ \ \ \ - SECRET_KEY=$secret\\
    " docker-compose.yml
# Remove created files
rm *.bak
