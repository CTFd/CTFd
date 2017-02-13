#!/bin/sh
# First, if a yaml file is passed in via environment variable, we
# auto-poulate from that.

if [ ! -z "$CTFD_YAML_FILE" ]; then
	if [ -e "$CTFD_YAML_FILE" ]; then
		python populate-yaml.py $CTFD_YAML_FILE;
	fi
fi

gunicorn --bind 0.0.0.0:8000 -w 4 'CTFd:create_app()'
