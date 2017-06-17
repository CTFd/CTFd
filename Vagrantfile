# -*- mode: ruby -*-
# vi: set ft=ruby :

# Install tmux and virtualenv to support development
$preProvision= <<SCRIPT
sudo apt-get install tmux virtualenvwrapper -y
SCRIPT

# Wrap provisioning script with a virutalenv for pip packages
$provision= <<SCRIPT
source /usr/share/virtualenvwrapper/virtualenvwrapper_lazy.sh
mkvirtualenv ctfd
workon ctfd
cd /vagrant
./prepare.sh
pip install -r development.txt
SCRIPT

# Start development server in a tmux session
$startServer= <<SCRIPT
source /usr/share/virtualenvwrapper/virtualenvwrapper_lazy.sh
workon ctfd
tmux new-session -d -n "server" -c "/vagrant" -s "server" "python serve.py"
SCRIPT

Vagrant.configure("2") do |config|
  # contrib-jessie64 supports synced folders
  config.vm.box = "debian/contrib-jessie64"

  # Create a private network, which allows host-only access to the machine
  config.vm.network "private_network", ip: "10.9.8.7"

  # Forward the default port for the development server to host machine
  config.vm.network "forwarded_port", guest: 4000, host: 4000

  # Pre-provision
  config.vm.provision "shell", inline: $preProvision
  
  # Provisioning scripts
  config.vm.provision "shell", inline: $provision, privileged: false

  # Start server in tmux session (every reboot)
  config.vm.provision "shell", inline: $startServer, privileged: false, run: "always"

end
