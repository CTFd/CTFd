#!/bin/sh
# First, if a yaml file is passed in via environment variable, we
# auto-poulate from that.

# http://stackoverflow.com/questions/25503412/how-do-i-know-when-my-docker-mysql-container-is-up-and-mysql-is-ready-for-taking#29793382
echo "Waiting on MySQL"
while ! mysqladmin ping -h db --silent; do
	# Show some progress
	echo -n '.';
	sleep 1;
done
echo "Ready"
# Give it another second.
sleep 1;

if [ ! -z "$CTFD_YAML_FILE" ]; then
	if [ -e "$CTFD_YAML_FILE" ]; then
		python populate-yaml.py $CTFD_YAML_FILE;
	fi
fi

gunicorn --bind 0.0.0.0:8000 -w 4 'CTFd:create_app()'
