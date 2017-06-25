#!/bin/bash


# setup system
add-apt-repository ppa:certbot/certbot -y
apt-get update -y
apt-get install mariadb-client gunicorn python-pip python-dev nginx git certbot -y
mkdir /var/nginx
chown www-data /var/nginx

# setup ctfd
git clone https://github.com/gambtho/CTFd.git /opt/ctfd
cd /opt/ctfd/CTFd/plugins
git clone https://github.com/CTFd/CTFd-S3-plugin
cd CTFd-S3-plugin
pip install -r requirements.txt
cd /opt/ctfd
pip install -r requirements.txt

# configure gunicorn
echo "${GUNICORN}" > /opt/ctfd/gunicorn.sh
chmod +x /opt/ctfd/gunicorn.sh
chown -R ubuntu:www-data /opt/ctfd
cp /opt/ctfd/aws/gunicorn.service /etc/systemd/system/
systemctl daemon-reload && systemctl start gunicorn
systemctl enable gunicorn

# configure nginx
cp /opt/ctfd/aws/nginx.conf /etc/nginx/sites-available/ctfd
ln -s /etc/nginx/sites-available/ctfd /etc/nginx/sites-enabled
systemctl restart nginx

# validate install
service gunicorn stop
service gunicorn start
curl localhost:8000 >> /opt/ctfd/smoke_test.txt

