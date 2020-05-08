#!/bin/bash
set -e

source .env

rm -rf "${SCHEMA_DB_DIR}/${1}"
mkdir -p "${SCHEMA_DB_DIR}/${1}"

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_DBNAME="${DB_NAME_DEV}" &&
    SQL_DBHOST="${DB_HOST_DEV}" &&
    SQL_DBPORT="${DB_PORT_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_DBNAME="${DB_NAME_PROD}" &&
    SQL_DBHOST="${DB_HOST_PROD}" &&
    SQL_DBPORT="${DB_PORT_PROD}"
fi

# generate diagram from DB
java -jar schemaspy-6.0.0.jar \
-t pgsql \
-u "${SQL_DBUSER}" \
-db "${SQL_DBNAME}" \
-host "${SQL_DBHOST}" \
-port "${SQL_DBPORT}" \
-s "${1}" \
-o "${SCHEMA_DB_DIR}/${1}"

echo "Diagram successfully generated in ${SCHEMA_DB_DIR}/${1}."
