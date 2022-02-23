#!/usr/bin/bash

# Pre-requisites
# - You've got heroku CLI installed somehow


# create DB URL - grab from the JAWSDB configured URL
#NEW_URL=`echo ${JAWSDB_MARIA_URL} | sed 's/mysql\:\/\//mysql+pymysql\:\/\//'`
#export DATABASE_URL="${NEW_URL}"

# create REDIS URL - grab from REDISTOGO
#export REDIS_URL="${REDISTOGO_URL}"

heroku login
heroku apps:create --region us
git push heroku main
APP_NAME=`git remote -v | grep 'heroku.*(fetch)$' | sed 's/.*\///' | sed 's/\.git.*//'`

heroku addons:destroy heroku-postgresql --confirm "${APP_NAME}"
heroku addons:create redistogo:nano
heroku addons:create jawsdb-maria:kitefin

echo "Sleeping for a moment"
sleep 15

NEW_DB_URL=`heroku config:get JAWSDB_MARIA_URL | sed 's/mysql\:\/\//mysql+pymysql\:\/\//'`
heroku config:set DATABASE_URL="${NEW_DB_URL}"

REDIS_URL=`heroku config:get REDISTOGO_URL`
heroku config:set REDIS_URL="${REDIS_URL}"

heroku ps:restart

echo "https://${APP_NAME}.herokuapp.com"