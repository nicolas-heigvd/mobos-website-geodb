#!/bin/bash
set -e

source .env

if [ ${ENV} = 'DEV' ]
then
    SQL_DBUSER="${DB_USER_DEV}" &&
    SQL_DBNAME="${DB_NAME_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_DEV}"

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBUSER="${DB_USER_PROD}" &&
    SQL_DBNAME="${DB_NAME_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_PROD}"
fi

bash "${PWD}"/00_init_modos_db.sh &&
bash "${PWD}"/01_reset_modos_db.sh &&
bash "${PWD}"/02_inject_osm_into_modos_db.sh &&
bash "${PWD}"/03_preprocess_modos_4pgr.sh &&
bash "${PWD}"/04_modos_routing.sh &&
bash "${PWD}"/05_modos_triggers.sh &&
bash "${PWD}"/06_sync_with_mobapp.sh &&
bash "${PWD}"/07_snap_observations_to_edges.sh
