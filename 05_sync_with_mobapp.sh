#!/bin/bash
set -e

eval $(egrep -v '^#' .env | xargs)

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_DEV}" &&
    SQL_FILE="${DB_05_SQLFILE_DEV}" &&
    PYTHON_SCRIPT="${PYTHON_SCRIPT_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_PROD}" &&
    SQL_FILE="${DB_05_SQLFILE_PROD}" &&
    PYTHON_SCRIPT="${PYTHON_SCRIPT_PROD}"
fi

psql "service=${SQL_SERVICE}" -v ON_ERROR_STOP=1 -v SQL_USER=${SQL_DBUSER} \
    -b -f ${SQL_FILE} &&
python3 "${PYTHON_SCRIPT}" -S

echo "MobApp data successfully imported."
