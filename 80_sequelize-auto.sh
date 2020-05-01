#!/bin/bash
set -e

eval $(egrep -v '^#' .env | xargs)

rm -rf "${SEQUELIZE_MODELS_DIR}/${1}"
mkdir -p "${SEQUELIZE_MODELS_DIR}/${1}"

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

# generate models from DB
sequelize-auto \
 -h "${SQL_DBHOST}" \
 -d "${SQL_DBNAME}" \
 -u "${SQL_DBUSER}" \
 -s "${1}" \
 -x "${DBPASS}" \
 -p "${SQL_DBPORT}" \
 -e postgres \
 -o "${SEQUELIZE_MODELS_DIR}"

echo "Model files successfully generated in ${SEQUELIZE_MODELS_DIR}."
