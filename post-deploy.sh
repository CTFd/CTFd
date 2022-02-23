#!/bin/sh
#
# create DB URL - grab from the JAWSDB configured URL
env DATABASE_URL=`echo ${JAWSDB_MARIA_URL} | sed 's/mysql\:\/\//mysql+pymysql\:\/\//'`
#
# create REDIS URL - grab from REDISTOGO
env REDIS_URL=`echo ${REDISTOGO_URL}`