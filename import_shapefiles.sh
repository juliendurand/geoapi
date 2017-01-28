#!/bin/sh

# get current working directory
MYPWD=$(pwd)

# drop all existing tables
psql -c "drop schema public cascade;"

# recreate the default schema
psql -c "create schema public;"

# import the postgis extension
psql -c "CREATE EXTENSION postgis;"

# dde_a
shp2pgsql -c -D -I ./data/zoniers/dde_a/zonier_final_ddea_a2_decoup.shp dde_a | psql > /dev/null

# dde_m
shp2pgsql -c -D -I ./data/zoniers/dde_m/zonier_final_ddem_fus.shp dde_m | psql > /dev/null

# bdg
shp2pgsql -c -D -I ./data/zoniers/bdg/zonier_BDG_decoup_total.shp bdg | psql > /dev/null

# clim
shp2pgsql -c -D -I ./data/zoniers/clim/Q95_XWS_polygone_lambert.shp clim | psql > /dev/null

# vol => csv table
psql -c "CREATE TABLE vol_f ( \
    CODE_COMM char(3), \
    INSEE_COM char(5) PRIMARY KEY, \
    NOM_COMM varchar, \
    X_CENTROID integer, \
    Y_CENTROID integer, \
    SUPERFICIE integer, \
    POPULATION real, \
    zone_vol_f smallint, \
    zone_vol_f_amelioree smallint \
);"
psql -c "CREATE TABLE vol_c ( \
    CODE_COMM char(3), \
    INSEE_COM char(5) PRIMARY KEY, \
    NOM_COMM varchar, \
    X_CENTROID integer, \
    Y_CENTROID integer, \
    SUPERFICIE integer, \
    POPULATION real, \
    zone_vol_c smallint, \
    zone_vol_c_amelioree smallint \
);"
psql -c "COPY vol_f FROM '$MYPWD/data/zoniers/vol/zonier_vol_f_insee.csv' DELIMITER ';' CSV HEADER;"
psql -c "COPY vol_c FROM '$MYPWD/data/zoniers/vol/zonier_vol_c_insee.csv' DELIMITER ';' CSV HEADER;"

# incattr => csv table
psql -c "CREATE TABLE incattr ( \
    DCOMIRIS char(9) PRIMARY KEY,
    NOM_IRIS varchar,
    DEPCOM char(5),
    COMMUNE varchar,
    CV char(4),
    DEP char(2),
    REG varchar,
    ERREUR varchar,
    zonier_inc smallint,
    zonier_i_1 smallint
);"
psql -c "COPY incattr FROM '$MYPWD/data/zoniers/incattr/zonier_incendie_iris.csv' DELIMITER ';' CSV HEADER;"

# catnat / sec
shp2pgsql -c -D ./data/zoniers/sec/SechV2.shp sec_tmp | psql > /dev/null
psql -c "CREATE TABLE sec AS (SELECT ST_Subdivide(geom, 50) AS geom, alea FROM sec_tmp);"
psql -c "DROP TABLE sec_tmp"
psql -c  "CREATE INDEX sec_idx ON sec USING GIST(geom);"

# catnat / flood
shp2pgsql -c -D ./data/zoniers/flood/Flood.shp flood_tmp | psql > /dev/null
psql -c "CREATE TABLE flood AS (SELECT ST_Subdivide(geom, 50) AS geom, zone_flood FROM flood_tmp);"
psql -c "DROP TABLE flood_tmp"
psql -c  "CREATE INDEX flood_idx ON flood USING GIST(geom);"

# catnat / coastal flood
shp2pgsql -c -D -I ./data/zoniers/coastal_flood/CoastalFR1.shp coastal_flood | psql > /dev/null

# print final statistics
psql -c "select relname, n_tup_ins - n_tup_del as rowcount from pg_stat_all_tables where relname not like '%pg_%' and relname not like '%sql_%';"
