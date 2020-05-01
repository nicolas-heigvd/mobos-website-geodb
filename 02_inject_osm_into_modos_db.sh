#!/bin/bash
set -e

eval $(egrep -v '^#' .env | xargs)

if [ ${ENV} = 'DEV' ]
then
    SQL_DBNAME="${DB_NAME_DEV}" &&
    SQL_SERVICE="${DB_SERVICE_DEV}" &&
    SHP_NODES_FILE=${ENV_SHP_DATA_SOURCE_NODES} &&
    SHP_EDGES_FILE="${ENV_SHP_DATA_SOURCE_EDGES}" &&
    GPKG_FILE=${ENV_GPKG_DATA_SOURCE}
    USE_GPKG=true

elif [ ${ENV} = 'PROD' ]
then
    SQL_DBNAME="${DB_NAME_PROD}" &&
    SQL_SERVICE="${DB_SERVICE_PROD}" &&
    SHP_NODES_FILE=${ENV_SHP_DATA_SOURCE_NODES} &&
    SHP_EDGES_FILE="${ENV_SHP_DATA_SOURCE_EDGES}" &&
    GPKG_FILE=${ENV_GPKG_DATA_SOURCE}
    USE_GPKG=true
fi


if [ "${USE_GPKG}" = false ]
then
    echo "Using Shapefiles in: ${BASEDIR_SHP}"
    ogr2ogr -append --config OGR_TRUNCATE YES --config PG_USE_COPY YES \
    -nln osmdata.osm_edges \
    -f "PostgreSQL" PG:"dbname=${SQL_DBNAME} service=${SQL_SERVICE}" \
    -a_srs EPSG:4326 "${SHP_EDGES_FILE}"
    echo "OSM edges successfully injected from SHP."

    ogr2ogr -append --config OGR_TRUNCATE YES --config PG_USE_COPY YES \
    -nln osmdata.osm_nodes \
    -f "PostgreSQL" PG:"dbname=${SQL_DBNAME} service=${SQL_SERVICE}" \
    -a_srs EPSG:4326 "${SHP_NODES_FILE}"
    echo "OSM nodes successfully injected from SHP."

# -nlt PROMOTE_TO_MULTI \
else
    echo "Using GeoPackage: ${GPKG_FILE}"
    ogr2ogr -append --config OGR_TRUNCATE YES --config PG_USE_COPY YES \
    -nln osmdata.osm_edges \
    -f "PostgreSQL" PG:"dbname=${SQL_DBNAME} service=${SQL_SERVICE}" \
    -a_srs EPSG:4326 "${GPKG_FILE}" "edges"
    echo "OSM edges successfully injected from GPKG."

    ogr2ogr -append --config OGR_TRUNCATE YES --config PG_USE_COPY YES \
    -nln osmdata.osm_nodes \
    -f "PostgreSQL" PG:"dbname=${SQL_DBNAME} service=${SQL_SERVICE}" \
    -a_srs EPSG:4326 "${GPKG_FILE}" "nodes"
    echo "OSM nodes successfully injected from GPKG."

fi

echo "GeoData successfully imported."
