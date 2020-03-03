#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main routine for retrieving reference MeteoSwiss data (e.g. CPC, RZC, POH, etc)
This is meant to be run as a command line command from a slurm script

i.e. ./retrieve_reference_data -t <task_file_name> -c <config_file_name>
- o <output_folder>

IMPORTANT: this function is called by the main routine in database.py
so you should never have to call it manually
--------------
Daniel Wolfensberger, LTE-MeteoSwiss, 2020
"""

import numpy as np
import pandas as pd
import datetime
import logging

import pysteps

logging.basicConfig(level=logging.INFO)
import os

from collections import OrderedDict
from optparse import OptionParser

from rainforest.common import constants
from rainforest.common.lookup import get_lookup
from rainforest.common.utils import read_task_file, envyaml
from rainforest.common.retrieve_data import retrieve_prod, retrieve_CPCCV
from rainforest.common.io_data import read_cart


class Updater(object):
    def __init__(self, task_file, config_file, output_folder):
        """
        Creates an Updater  class instance that allows to add new reference
        data to the database
        
        Parameters
        ----------
        task_file : str
            The full path to a task file, i.e. a file with the following format
            timestamp, station1, station2, station3...stationN
            These files are generated by the database.py module so normally youretrieve_CPCCV
            shouldn't have to create them yourself
        config_file : str
            The full path of a configuration file written in yaml format
            that indicates how the radar retrieval must be done
        output_folder: str
            The full path where the generated files will be stored
        """
        
        self.config = envyaml(config_file)
        self.tasks = read_task_file(task_file)
        self.output_folder = output_folder
        
        self.ref_config = self.config['REFERENCE_RETRIEVAL']
        self.neighb_x = self.ref_config['NEIGHBOURS_X']
        self.neighb_y = self.ref_config['NEIGHBOURS_Y']
        self.products = self.ref_config['PRODUCTS']
        # Decompose motion vectors variables
        products_decomposed = []
        for prod in self.products:
            if 'MV' in prod:
                products_decomposed.append(prod + '_x')
                products_decomposed.append(prod + '_y')
            else:
                products_decomposed.append(prod)
        self.products = products_decomposed
        self.dims = {'np': len(self.products),
                     'nnx': len(self.neighb_x),
                     'nny': len(self.neighb_y)}
        
    def retrieve_cart_files(self, start_time, end_time, products):
        """
        Retrieves a set of reference product files for a given time range
        
        Parameters
        ----------
        start_time : datetime.datetime instance
            starting time of the time range
        end_time : datetime.datetime instance
            end time of the time range
        products : list of str
            list of all products to retrieve, must be valid MeteoSwiss product
            names, for example CPC, CPCH, RZC, MZC, BZC, etc
        """
        
        files_allproducts = {}

        for prod in products:
            try:
                if prod == 'CPC' or prod == 'CPCH':
                    files = retrieve_prod(self.config['TMP_FOLDER'],
                                                 start_time, end_time, prod, 
                                                 pattern = '*5.801.gif')
                else:
                    files = retrieve_prod(self.config['TMP_FOLDER'],
                                                 start_time, end_time, prod)
              
                files_allproducts[prod] = files
            except:
                logging.error("""Retrieval for product {:s} at timesteps {:s}-{:s} 
                          failed""".format(prod, str(start_time), 
                                                 str(end_time)))
                files_allproducts[prod] = []
                
        return files_allproducts

    def process_all_timesteps(self):
        """
        Processes all timestaps in the task file
        """
        
        # Get relevant parameters from user config
        fill_value = self.config['NO_DATA_FILL']
        nneighb = self.dims['nnx'] * self.dims['nny']
        logging.info('Products: '+','.join(self.products))
        logging.info('Nx      : '+','.join([str(n) for n in self.neighb_x]))
        logging.info('Ny      : '+','.join([str(n) for n in self.neighb_y]))
             

        # All 10 min timestamps to process (gauge data)
        all_timesteps = list(self.tasks.keys())
        
        # LUT to get cartesian data at gauge
        lut_cart = get_lookup('station_to_qpegrid')
        
        # Initialize output
        data_10minagg = [] # Contains all 10 min data for all products
        data_cst = [] # for time, sta, nx,ny
        
        if 'CPC.CV' in self.products:
            data_cpccv = [] # separate list for cpccv
            data_cst_cpccv = [] # for time, sta, nx,ny
            include_cpccv = True
            current_hour = True
            self.products.remove('CPC.CV')
            colnames_cpccv = ['TIMESTAMP','STATION','NX','NY']
            colnames_cpccv.append('CPC.CV')
        
         
        # For motion vectors
        oflow_method = pysteps.motion.get_method(self.ref_config['MV_METHOD'])
        
        colnames = ['TIMESTAMP','STATION','NX','NY']
        colnames.extend(self.products)
        
        for i, tstep in enumerate(all_timesteps):
            logging.info('Processing timestep '+str(tstep))
            
            # retrieve radar data
            tstart = datetime.datetime.utcfromtimestamp(float(tstep))
            tend = tstart + datetime.timedelta(minutes = 5) 
            
            tstep_end = tstep + 10 * 60 # 10 min
            
            stations_to_get = self.tasks[tstep]
            
            hour_of_year = datetime.datetime.strftime(tstart,'%Y%m%d%H')
            day_of_year = hour_of_year[0:-2]
            
            if i == 0:
                current_day = day_of_year
        
            if day_of_year != current_day or i == len(all_timesteps) - 1:
                logging.info('Saving new table for day {:s}'.format(str(current_day)))
                data_10minagg = np.array(data_10minagg)
                data_cst = np.array(data_cst)
                # Concatenate metadata and product data
                all_data = np.hstack((data_cst, data_10minagg))
                dic = OrderedDict()
                
                for c, col in enumerate(colnames):
                    data_col = all_data[:,c]
                    isin_listcols = [col in c for c in constants.COL_TYPES.keys()]
                    if any(isin_listcols):
                        idx = np.where(isin_listcols)[0][0]
                        coltype = list(constants.COL_TYPES.values())[idx]
                        try:
                            data_col = data_col.astype(coltype)
                        except:# for int
                            data_col = data_col.astype(np.float).astype(coltype)
                    else:
                        data_col = data_col.astype(np.float32)
                    dic[col] = data_col
             
                df = pd.DataFrame(dic)
       
                if include_cpccv:
                    data_cst_cpccv = np.array(data_cst_cpccv)
                    data_cpccv = np.array([data_cpccv]).T
                    all_data_cpccv = np.hstack((data_cst_cpccv, data_cpccv))
                    
                    dic = OrderedDict()
                    for c, col in enumerate(colnames_cpccv):
                        data_col = all_data_cpccv[:,c]
                        isin_listcols = [col in c for c 
                                             in constants.COL_TYPES.keys()]
                        if any(isin_listcols):
                            idx = np.where(isin_listcols)[0][0]
                            coltype = list(constants.COL_TYPES.values())[idx]
                            try:
                                data_col = data_col.astype(coltype)
                            except:# for int
                                data_col = data_col.astype(np.float).astype(coltype)
                        else:
                            data_col = data_col.astype(np.float32)
                        dic[col] = data_col
                    
                               
                    dfcpc = pd.DataFrame(dic)
                    df = pd.merge(df, dfcpc, 
                                  on = ['STATION','TIMESTAMP','NX','NY'],
                                  how = 'left')
                    
                name = self.output_folder + current_day + '.parquet'
                logging.info('Saving file ' + name)
                df.to_parquet(name, compression = 'gzip', index = False)
                
                current_day = day_of_year
                # Reset lists
                  
                data_10minagg = [] # separate list for cpccv
                data_cst = [] # for time, sta, nx,ny
                if include_cpccv:
                    data_cpccv = [] # separate list for cpccv
                    data_cst_cpccv = [] # for time, sta, nx,ny
                    
            if include_cpccv:
                if hour_of_year != current_hour:
                    current_hour = hour_of_year
                    
                    data_at_stations = retrieve_CPCCV(tend, stations_to_get)
                    data_at_stations[np.isnan(data_at_stations)] = fill_value
                    # Assign CPC.CV values to rows corresponding to nx = ny = 0
                    data_cpccv.extend(data_at_stations)
                  
                    for sta in stations_to_get:
                        data_cst_cpccv.append([tstep_end, sta, 0,0]) # nx = ny = 0
                            
          
            # Initialize output
            N,M = len(stations_to_get) * nneighb, self.dims['np']
            data_allprod = np.zeros((N,M), dtype = np.float32) + np.nan
            
            # Get data
            baseproducts = [prod for prod in self.products if 'MV' not in prod]
            allfiles = self.retrieve_cart_files(tstart, tend, baseproducts)
            
            for j, prod in enumerate(self.products):
                logging.info('Retrieving product ' + prod)
                if 'MV' in prod:
                    if '_x' in prod:
                        idx_slice_mv = 0
                        # Motion vector case
                        ###################
                        # Get product for which to compute MV
                        baseprod = prod.strip('MV').split('_')[0]
                        # Initialize output
                        N = len(stations_to_get) * nneighb
                        data_prod = np.zeros((N,), dtype = np.float32) + np.nan
                        
                        try:
                            # For CPC we take only gif
                            files  = allfiles[baseprod]
                            
                            R = []
                            for f in files:
                                R.append(read_cart(f))
                            R = np.array(R)
                            R[R<0] = np.nan
                            mv = oflow_method(R)
                            
                            # Mask mv where there is no rain
                            mask = np.nansum(R, axis = 0) <= 0
                            mv[:,mask] = 0
                        except:
                            # fill with missing values, we don't care about the exact dimension
                            mv = np.zeros((2,1000,1000)) + fill_value 

                    elif '_y' in prod: # mv already computed
                        idx_slice_mv = 1 
                        
                    idx_row = 0 # Keeps track of the row
                    for sta in stations_to_get: # Loop on stations
                        for nx in self.neighb_x:
                            for ny in self.neighb_y:
                                strnb = '{:d}{:d}'.format(nx,ny)
                                # Get idx of Cart pixel in 2D map
                                idx = lut_cart[sta][strnb]
                                data_prod[idx_row] = mv[idx_slice_mv, idx[0],
                                                                idx[1]]
                                idx_row += 1

                else:
                    # Normal product case
                    ###################
                    files = allfiles[prod]
                    
                    # Initialize output
                    N,M = len(stations_to_get) * nneighb, len(files)
                    data_prod = np.zeros((N,M), dtype = np.float32) + np.nan
                    
                    
                    for k, f in enumerate(files):
                        try:
                            proddata = read_cart(f)
                        except:
                            # fill with missing values, we don't care about the exact dimension
                            proddata = np.zeros((1000,1000)) + np.nan
                            
                        # Threshold radar precip product
                        if prod == 'RZC' or prod == 'AQC':
                            proddata[proddata < constants.MIN_RZC_VALID] = 0
                            
                        idx_row = 0 # Keeps track of the row
                        for sta in stations_to_get: # Loop on stations
                            for nx in self.neighb_x:
                                for ny in self.neighb_y:
                                    strnb = '{:d}{:d}'.format(nx,ny)
                                    # Get idx of Cart pixel in 2D map
                                    idx = lut_cart[sta][strnb]
                                    data_prod[idx_row,k] = proddata[idx[0],
                                                                    idx[1]]
                           
                                    idx_row += 1
                                                
                    data_prod = np.nanmean(data_prod,axis = 1)
                    data_prod[np.isnan(data_prod)] = fill_value
                    
                data_allprod[:,j] = data_prod
            
            for prod in allfiles.keys():
                for f in allfiles[prod]:
                    try:
                        os.remove(f)
                    except:
                        pass
                    
            data_10minagg.extend(data_allprod)
    
            # Add constant data
            for sta in stations_to_get:
                for nx in self.neighb_x:
                    for ny in self.neighb_y:
                        data_cst.append([tstep_end, sta,nx,ny])
                         
             
if __name__ == '__main__':
    parser = OptionParser()
    
    parser.add_option("-c", "--configfile", dest = "config_file",
                      help="Specify the user configuration file to use",
                      metavar="CONFIG")
    
    
    parser.add_option("-t", "--taskfile", dest = "task_file", default = None,
                      help="Specify the task file to process", metavar="TASK")
    
    parser.add_option("-o", "--output", dest = "output_folder", default = '/tmp/',
                      help="Specify the output directory", metavar="FOLDER")
    
    (options, args) = parser.parse_args()
    
    
    u = Updater(options.task_file, options.config_file, options.output_folder)
    u.process_all_timesteps()
