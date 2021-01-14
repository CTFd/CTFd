#!/bin/bash

# Script to install docker in Debian Guest VM
# per: https://docs.docker.com/engine/installation/linux/debian/#install-docker-ce

# Install packages to allow apt to use a repository over HTTPS
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python-pip \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Set up the stable repository. 
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Update the apt package index
sudo apt-get update

# Install the latest version of Docker
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce

# Add user to the docker group
# Warning: The docker group grants privileges equivalent to the root user. 
sudo usermod -aG docker ${USER}

# Configure Docker to start on boot
sudo systemctl enable docker

# Install docker-compose
pip install docker-compose
