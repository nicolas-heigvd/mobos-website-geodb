#!/bin/bash
set -e

source .env

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_DEV}" &&
    SQL_FILE="${DB_01_SQLFILE_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_PROD}" &&
    SQL_FILE="${DB_01_SQLFILE_PROD}"
fi

echo ${SQL_FILE}
psql "service=${SQL_SERVICE}" -v ON_ERROR_STOP=1 -v SQL_USER=${SQL_DBUSER} \
-b -f "${SQL_FILE}"

echo "Database tables successfully created."