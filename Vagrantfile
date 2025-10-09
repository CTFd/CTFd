# -*- mode: ruby -*-
# vi: set ft=ruby :

# BOX_IMG = "generic/ubuntu1810" # Working  
BOX_IMG = "ubuntu/bionic64" # Unable to ssh
# BOX_IMG = "generic/ubuntu1804" # Working
# BOX_IMG = "generic/ubuntu2004" # ssh problem

# Install tmux, virtualenv, and mariadb-server to support development
$preProvision= <<SCRIPT
# Prevent attempt to access stdin, causing dpkg-reconfigure error output
export DEBIAN_FRONTEND=noninteractive

# Installation kept failing due to python 2.
# Changing default python to 3.
apt -y update
apt -y upgrade
apt -y install python3-pip
update-alternatives --install /usr/bin/python python /usr/bin/python3 10
python -m pip install --upgrade pip
python -m pip install virtualenvwrapper

# As per instructions at https://downloads.mariadb.org/mariadb/repositories
apt-get install -y software-properties-common
apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 2>&1
add-apt-repository -y 'deb [arch=amd64,arm64,i386,ppc64el] http://mirror.lstn.net/mariadb/repo/10.4/ubuntu xenial main'
apt-get update
apt-get install -y mariadb-server
apt-get install -y tmux virtualenvwrapper
SCRIPT

# Wrap provisioning script with a virutalenv for pip packages
$provision= <<SCRIPT
source /usr/share/virtualenvwrapper/virtualenvwrapper_lazy.sh
mkvirtualenv ctfd
workon ctfd
cd /vagrant
./prepare.sh
pip install -r development.txt

echo "Initialising database"
commands="CREATE DATABASE ctfd;
CREATE USER 'ctfduser'@'localhost' IDENTIFIED BY 'ctfd';
GRANT USAGE ON *.* TO 'ctfduser'@'localhost' IDENTIFIED BY 'ctfd';
GRANT ALL privileges ON ctfd.* TO 'ctfduser'@'localhost';FLUSH PRIVILEGES;"
echo "${commands}" | sudo /usr/bin/mysql -u root -pctfd
SCRIPT

# Start development server in a tmux session
$startServer= <<SCRIPT
source /usr/share/virtualenvwrapper/virtualenvwrapper_lazy.sh
workon ctfd

export DATABASE_URL="mysql+pymysql://ctfduser:ctfd@localhost/ctfd"

cd /vagrant
python manage.py db upgrade

echo "Starting CTFd"
tmux new-session -d -n "ctfd" -c "/vagrant" -s "ctfd" "gunicorn --bind 0.0.0.0:8000 -w 4 'CTFd:create_app()'"
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = BOX_IMG

  # Create a private network, which allows host-only access to the machine
  config.vm.network "private_network", ip: "10.9.8.7"

  # Forward the default port for the development server (4000)
  # and docker or gunicorn (8000) to host machine
  config.vm.network "forwarded_port", guest: 4000, host: 4000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.synced_folder ".", "/vagrant"
  
  # Fix ssh problem
  config.vm.provision :shell, :inline => "sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config; sudo systemctl restart sshd;", run: "always"

  # Pre-provision
  config.vm.provision "shell", inline: $preProvision

  # Provisioning scripts
  config.vm.provision "shell", inline: $provision, privileged: false

  # Start server in tmux session (every reboot)
  config.vm.provision "shell", inline: $startServer, privileged: false,
                      run: "always"

  # Install docker (convenience)
  config.vm.provision "shell", path: "scripts/install_docker.sh", privileged: false
end
