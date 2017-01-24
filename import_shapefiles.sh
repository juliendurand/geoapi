#!/bin/sh
psql -c "drop schema public cascade;create schema public;CREATE EXTENSION postgis;"
shp2pgsql -c -D -I ./data/zoniers/ddea/zonier_final_ddea_a2_decoup.shp dde_a | psql > /dev/null
