#!/bin/bash
set -e

eval $(egrep -v '^#' .env | xargs)

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_DEV}" &&
    SQL_FILE_PRE="${DB_06_SQLFILE_PRE_DEV}" &&
    SQL_FILE_POST="${DB_06_SQLFILE_POST_DEV}" &&
    PYTHON_SCRIPT="${PYTHON_SCRIPT_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_PROD}" &&
    SQL_FILE_PRE="${DB_06_SQLFILE_PRE_PROD}" &&
    SQL_FILE_POST="${DB_06_SQLFILE_POST_PROD}" &&
    PYTHON_SCRIPT="${PYTHON_SCRIPT_PROD}"
fi

echo ${SQL_FILE}
psql "service=${SQL_SERVICE}" -v ON_ERROR_STOP=1 -v SQL_USER=${SQL_DBUSER} \
    -b -f ${SQL_FILE_PRE} &&
python3 "${PYTHON_SCRIPT}" -S &&
psql "service=${SQL_SERVICE}" -v ON_ERROR_STOP=1 -v SQL_USER=${SQL_DBUSER} \
    -b -f ${SQL_FILE_POST}

echo "MobApp data successfully imported."
