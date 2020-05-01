#!/bin/bash
set -e
USE_PG=false

eval $(egrep -v '^#' .env | xargs)

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_DBNAME_NEW="${DB_NAME_NEW_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_RESTORE_DEV}" &&
    SQL_DUMP_FILE="${DB_DUMP_FILE_SQL_DEV}" &&
    BKP_DUMP_FILE="${DB_DUMP_FILE_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_DBNAME_NEW="${DB_NAME_NEW_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_RESTORE_PROD}" &&
    SQL_DUMP_FILE="${DB_DUMP_FILE_SQL_PROD}" &&
    BKP_DUMP_FILE="${DB_DUMP_FILE_PROD}"
fi

echo "Restoring database in new ${SQL_DBNAME_NEW}..."

dropdb -U "${SQL_DBUSER}" --if-exists "${SQL_DBNAME_NEW}" || true
createdb -U "${SQL_DBUSER}" "${SQL_DBNAME_NEW}" --owner="${SQL_DBUSER}"
# remove -h localhost if using peer auth
if [ "${USE_PG}" = 'true' ]
then
    echo "Using pg_retore tool..."
    pg_restore -U "${SQL_DBUSER}" -d "${SQL_DBNAME_NEW}" "${BKP_DUMP_FILE}"
else
    echo "Using psql..."
    psql "service=${SQL_SERVICE}" -v ON_ERROR_STOP=1 \
    -b -f "${SQL_DUMP_FILE}"
fi

echo "Restoration done."
