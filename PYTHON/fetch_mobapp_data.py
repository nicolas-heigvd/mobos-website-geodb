#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 13:08:59 2020

@author: nicolas.blanc

MIT License

Copyright (c) 2020 Nicolas Blanc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Except as contained in this notice, the name of Nicolas Blanc shall not be
used in advertising or otherwise to promote the sale, use or other dealings
in this Software without prior written authorization from Nicolas Blanc.
"""
###############################################################################
# IMPORTS
###############################################################################
#%%
from __future__ import absolute_import
import os, sys, gc
from os import getcwd
from os.path import dirname, basename, abspath
from datetime import datetime
from time import time
import argparse
import math
import requests
import json
import numpy as np
import pandas as pd
import pyproj
import psycopg2
from sqlalchemy import create_engine
from shapely.geometry import Point
import geopandas as gpd
from folium import Map, Marker, Icon, DivIcon
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv()

#%%
###############################################################################
vers = "1.0.0"
parser = argparse.ArgumentParser()
parser.add_argument("-V", "--version",
                    help="show program version", action="store_true")
parser.add_argument("-D", "--debug",
                    help="set debug mode, default=True", action="store_true")
parser.add_argument("-S", "--sync",
                    help=("sync postgres table with mobapp structure.'"),
                    action="store_true")

args = parser.parse_args()

if args.version:
    print("Program version is: {}".format(vers))

#__file__ = os.path.join(os.getcwd(),'datamodel')
#%%
###############################################################################
# TRIGGERS AND CONSTANTS
###############################################################################
DEBUG = bool(args.debug)
SYNC = bool(args.sync)

TAB_HEAD = ["observations", "events"]

env_path = os.path.join(dirname(dirname(abspath(__file__))),'.env')
env_json_path = os.path.join(dirname(dirname(abspath(__file__))),'.env.json')
load_dotenv(dotenv_path=env_path)

ENV_KEYS = (
    "ENV",
    "ENV_SHP_DATA_SOURCE", 
    "ENV_GPKG_DATA_SOURCE",
    "PROD_DATA_SOURCE",
    "DEBUG",
    "SOCKET",
    "API_ENDPOINT",
)

ENV_PARAMS = {key: None for key in ENV_KEYS}
for k,v in ENV_PARAMS.items():
    ENV_PARAMS[k] = os.getenv(k)

with open(env_json_path) as json_file:
    ENV_JSON = json.load(json_file)
#%%
###############################################################################
# DB connection function
###############################################################################
#%%
def getConnectors(modos_geo=True):
    env_path = os.path.join(dirname(getcwd()),'.env')
    load_dotenv(dotenv_path=env_path)
    env = os.getenv("ENV")
    DEBUG = False
    if os.getenv("DEBUG").lower()=='true':
        DEBUG = True
    if DEBUG:
        print(("Environment is set to: {} "
               "in file {}").format(env, basename(__file__)))
    SOCKET = os.getenv("SOCKET").capitalize()
    DB_KEYS = ("DB_USER", "DB_PASS", "DB_HOST", "DB_PORT", "DB_NAME")
    PG_KEYS = ("user", "password", "host", "port", "dbname")
    if SOCKET=='True':
        DB_KEYS=DB_KEYS[0],*DB_KEYS[3:]
        PG_KEYS = PG_KEYS[0],*PG_KEYS[3:]
    if env=='DEV':
        DB_KEYS_MDS = tuple([k+"_"+env for k in DB_KEYS])
    elif env=='PROD':
        DB_KEYS_MDS = tuple([k+"_"+env for k in DB_KEYS])
    
    del(DB_KEYS)
     
    DB_PARAMS_MDS = {key: None for key in DB_KEYS_MDS}
    for k,v in DB_PARAMS_MDS.items():
        DB_PARAMS_MDS[k] = os.getenv(k)

    # Generate connection string for the modos database:  
    if True:
        DB_MDS = {key:val for key,val in zip(PG_KEYS, DB_PARAMS_MDS.values())}
        if True: # use peer with libpq
            del(DB_MDS['password'])
    
    def connector_MDS():
        return psycopg2.connect(**DB_MDS)
     
    retval = None
    if modos_geo:
        retval = connector_MDS
        
    return(retval)
###############################################################################
#%%
def get_data_from_API(name='observations', USE_LOGIN=True):
    """ Docstring
    """
    if name not in ["observations", "events", "users"]:
        print("Wrong name. Existing.")
        return

    if USE_LOGIN:
        res0 = requests.post(
                   os.path.join(os.getenv("API_ENDPOINT"),
                                'authenticate'),
                   headers=ENV_JSON['head'],
                   json=ENV_JSON["modos_auth_params"],
                   )

    token = res0.json()['token']
    head = ENV_JSON['head']
    head['Authorization'] = "Bearer "+token

    res1 = requests.get(
               os.path.join(os.getenv("API_ENDPOINT"),
                            name),
               headers=head,
               params=ENV_JSON['modos_params'],
               )

    df1 = pd.DataFrame.from_dict(pd.json_normalize(res1.json()))
    if name == 'observations':
        df1.dropna(subset=['location.longitude','location.latitude'], inplace=True)
        
    return(df1)
###############################################################################   
#%%
def plot_map(df):
    """Docstring
    """
    print("Plotting points on Folium...")
    cmap = plt.get_cmap('gnuplot2')
    cmaplist = [cmap(i) for i in range(cmap.N)]
    keys =  list(df['description.obstacle'].unique())
    idx = np.arange(0,255,256/len(keys)).astype(np.int)
    cmapsublist = [cmaplist[i] for i in idx]
    cmapsublist = [tuple([int(255*el) for el in r]) for r in cmapsublist]
    colorsd = dict(zip(keys, cmapsublist))
    df['rgb'] = df['description.obstacle'].map(colorsd)
    df['hex'] = df['rgb'].map(lambda rgb: '#%02x%02x%02x%02x' % rgb)
    dfp = df[['location.longitude','location.latitude','description.obstacle','hex']].copy()
    dfp.dropna(axis=0, subset=['location.longitude','location.latitude'], inplace=True)
    m = Map(location=[46.77853, 6.64097],
            width=750, height=500, zoom_start=18,
            tiles='CartoDB positron')
    tooltip = 'Click me!'
    
    # &#9855; # wheelchair ascii '<i class="fa fa-map-marker fa-4x"></i>'
    for i,(lat, lon, obst, col) in dfp.iterrows():
        Marker(location=tuple((lon,lat)),
               icon=Icon(
                   color='blue',
                   icon_color=col,
                   icon='wheelchair',
                   angle=0,
                   prefix='fa'
               ),
               popup='<b>MoDoS observation<br>{}</b>'.format(i),
               tooltip=tooltip).add_to(m)
    print("Points plotted successfully!")
    
    if False:
        icon=Icon(
            color='black',
            icon_color=col,
            icon='wheelchair',
            angle=0,
            prefix='fa'
        )
        icon=DivIcon(
            icon_size=(16, 16),
            icon_anchor=(0, 0),
            html=f"""<div style=font-size:12pt;color:{col}><i class='fa fa-wheelchair fa-2x'></i></div>"""
        )

        
    return(m)
###############################################################################   
#%%
def get_tables_headers(name='observations'):
    """Docstring
    """
    if name not in ["observations", "events", "users"]:
        print("Wrong name. Exiting.")
        return
    connector_MDS = getConnectors()
    conn  = connector_MDS()
    curs  = conn.cursor()
    getHeaders = ("SELECT * FROM mobapp.{} LIMIT 0".format(name))
    curs.execute(getHeaders)
    conn.commit()
    colnames = []
    colnames = [desc[0] for desc in curs.description]
    print("There is {} columns:\n{}".format(len(colnames),colnames))
    
    return(colnames)
    
###############################################################################   
#%%   
def upsert_mobapp_data_to_postgres(df, name='observations'):
    """Docstring
    """
    # create temporary table?
    if name not in ["observations", "events", "users"]:
        print("Wrong name. Existing.")
        return

    connector_MDS = getConnectors()
    cols = list(df.columns)
    nbCols = len(cols)
    for idx, row in df.iterrows():
        query_string = ("INSERT INTO "+"mobapp.{}".format(name)+
            "("+nbCols*'%s '+") "
            "VALUES ("+nbCols* '%s ' +") "
            "ON CONFLICT (%s) DO "
            "UPDATE "
            "SET "
            "("+(nbCols)*'%s '+") = "
            "("+(nbCols)*'%s '+") "
            "WHERE %s = %s")
        sql_query = query_string
        
        with connector_MDS() as conn:
            with conn.cursor() as curs:
                # table names get singles quoted ?! ffs !!!
                print(curs.mogrify(sql_query,
                                   ((*cols,*row,cols[0],*cols,*row,cols[0],row[0]))))
                curs.execute(sql_query, ((*cols,*row,cols[0],*cols,*row,cols[0],row[0])))

    return(True)
#%%
def update_column_names(df, name='observations'):
    """Docstring
    """
    # change columns name to actually match the actual db:
    df.columns = '_mobapp_'+df.columns
    df.columns = df.columns.str.replace('__','_').str.replace('.','_').str.lower()
    
    return(df)
#%%   
def upload_mobapp_data_to_postgres(df, name='observations', delete_before=False):
    """ Docstring
    """
    if name not in ["observations", "events", "users"]:
        print("Wrong name. Existing.")
        return

    connector_MDS = getConnectors()
    engine = create_engine('postgresql+psycopg2://', creator=connector_MDS)
    if delete_before:
        print("Deleting ALL records from table mobapp.{}".format(name))
        drop_string = """DELETE FROM mobapp.{}""".format(name)+"""
                         WHERE id >0; """
        with connector_MDS() as conn:
            with conn.cursor() as curs:
                curs.execute(drop_string)
        
    # 'append' keeps the structure, 'replace' not (drop before):
    with engine.connect() as connection:       
        df.to_sql(name=name,
                  con=connection,
                  schema='mobapp',
                  if_exists='append', 
                  index=False)
    
    print("\"{}\" data successfully uploaded.".format(name))

    return(True)
###############################################################################   
#%%
def sync_all(tables_headers=TAB_HEAD):
    """Docstring
    """
    tables = {tab: None for tab in tables_headers}
    for key in tables:
        print("Processing table {}...".format(key))
        tables[key] = get_tables_headers(name=key)
        df = get_data_from_API(name=key)
        #print("len df: {}".format(len(df.columns)))
        df = update_column_names(df,name=key)
        for col in df.columns:
            if col.lower() not in tables[key]:
                print(("Oops, column {} not in table... Exiting." ).format(col))
                return
        #tables[key] = df
        UPSERT = False
        if not UPSERT:
            # table mobapp.* are truncated before INSERT.
            upload_mobapp_data_to_postgres(df, name=key, delete_before=True)
            print("Table {} successfully updated.".format(key))
        else:
            upload_mobapp_data_to_postgres(df, name=key)
            print("Blah.....................".format(key))

    print("All data successfully uploaded.")

    return(True)
#%%
if SYNC:
    sync_all()
