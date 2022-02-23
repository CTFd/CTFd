#!/bin/sh
#
# create DB URL - grab from the JAWSDB configured URL
NEW_URL=`echo ${JAWSDB_MARIA_URL} | sed 's/mysql\:\/\//mysql+pymysql\:\/\//'`
env DATABASE_URL="${NEW_URL}"
#
# create REDIS URL - grab from REDISTOGO
env REDIS_URL="${REDISTOGO_URL}"