###### OCA Pretrial Data - Standalone Data Scrapper ######
# Pretrial data released 07/2021 and every 6 months thereafter
# Python 2.7 script to scrape this data from the OCA site.
# Jeff Shamp - Bxd Data - 7/2021


###### FUTURE WARNING - The data file name is overly long ######
# and specifies the current year of relase (e.g., 2020). 
# This file name may change significantly in later data releases.
# Changes to the link or file reader may need admending if a name 
# change occurs on OCAs end. 

import requests
import zipfile
import pandas as pd
import numpy as np
from zipfile import ZipFile
from StringIO import StringIO
import urllib2
import fnmatch
import csv
import os
import boto3
import botocore
import psycopg2
import time
import warnings
from oca_utils.oca_utils import *

warnings.simplefilter(action='ignore', category=FutureWarning)

# URL building
today_str = time.strftime("%Y-%m-%d")
link_url= "http://www.nycourts.gov/"
link_subpath= "LegacyPDFS/court-research/"
link_file= "PretrialReleaseDataExtractWeb2020.zip"
link_url= link_url+link_subpath+link_file

# Try link for downloadable content - based on header information
try:
    is_downloadable(link_url)
    print("[Pretrial Release] - Vaild URL. Reading data.")
except requests.ConnectionError as exception:
    print("[Pretrial Release] - Not a valid URL.")
else:
# Get zip file and unpack
    print("[Pretrial Release] - Unzipping files {}" \
              .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
    r = urllib2.urlopen(link_url).read()
    file_ex = ZipFile(StringIO(r))
    file_ex.extractall()
    # pattern changes \/\/\/
    pattern = "*-revisedWO.csv"
    # Search the zip file directory for above pattern
    # Read the csv that matches the file.
    # This will likely change since the file name is long
    print("[Pretrial Release] - Reading CSV {}".format(time.strftime("%Y-%m-%d:%H:%M:%S")))
    for root, dirs, files in os.walk(os.getcwd(),):
        for filename in fnmatch.filter(files, pattern):
           # chunks = pd.read_csv(filename, chunksize=50000)
           # pretrial = pd.concat(chunks)
            pretrial_csv = file_ex.open(filename)
            pretrial = pd.read_csv(pretrial_csv)
    print("[Pretrial Release] - CSV file read {}" \
                      .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
del file_ex


###### FUTURE WARNING - This process (below) takes a while. 
# May be too much ec2 at some point depending on size of file. 

try:
    isinstance(pretrial, pd.DataFrame)
except: 
    print("[Pretrial Release] - No dataframe present")
else:
    print("[Pretrial Release] - Cleaning Data")

    # Format columns, re-assign dates
    pretrial.columns = pretrial.columns.str.lower()
    pretrial.columns = pretrial.columns.str.replace(" ", "_")
    pretrial.columns = pretrial.columns.str.replace("-", "_")
    date_cols = [col for col in pretrial.columns if col.endswith('_date')]
    not_date_type = ["rearrest_date"]
    for col in date_cols:
        if col in not_date_type:
            # fix Mar2020 format type
            pretrial[col] = pd.to_datetime(pretrial[col],format="%b%Y")
        # assign datetime to all other date columns
        pretrial[col] = pd.to_datetime(pretrial[col],errors='coerce')


    # Clean text columns
    for col in pretrial:
        if pretrial[col].dtype == "O":
            pretrial[col] = pretrial[col].str.lower()
    # Extract subsections from arraign, arrest, and conviction top charges
    arraign = pretrial["top_charge_at_arraign"] \
        .str.extract(r'((\d+) (\w+) (\w+))') \
        .rename(columns = {0:"full", 1:"section",2:"subsection",3:"charge"})
    arrest = pretrial["top_charge_at_arrest"] \
        .str.extract(r'((\d+) (\w+) (\w+))') \
        .rename(columns = {0:"full", 1:"section",2:"subsection",3:"charge"})
    convict = pretrial["top_charge_at_conviction"] \
        .str.extract(r'((\d+) (\w+) (\w+.{3}))') \
        .rename(columns = {0:"full", 1:"section",2:"subsection",3:"charge"})
    
    # make new columns for subsections
    print("[Pretrial Release] - Creating subsection columns")
    pretrial["arraign_subsection_bxd"] = arraign['subsection']
    pretrial["arrest_subsection_bxd"] = arrest['subsection']
    pretrial["conviction_subsection_bxd"] = convict['subsection']
    del arraign
    del arrest
    del convict

    # get law code weights for further filter of the subsection
    weights = pretrial.top_charge_weight_at_arraign.unique()

    # clean subsection using function `clean_subsection` see `oca_utils.py`
    pretrial.arraign_subsection_bxd = pretrial.arraign_subsection_bxd \
        .apply(lambda x:clean_subsection(x, weights))
    pretrial.arrest_subsection_bxd = pretrial.arrest_subsection_bxd \
        .apply(lambda x:clean_subsection(x, weights))
    pretrial.conviction_subsection_bxd = pretrial.conviction_subsection_bxd \
        .apply(lambda x:clean_subsection(x, weights))

    # break out new columns for article and section
    print("[Pretrial Release] - Splitting article and section")
    pretrial[["arraign_article_bxd", "arraign_section_bxd"]] = \
                pretrial.top_arraign_article_section.str.split(".",
                                                               n=1,
                                                               expand=True)
    pretrial[["arrest_article_bxd", "arrest_section_bxd"]] = \
                pretrial.top_arraign_article_section.str.split(".",
                                                               n=1,
                                                               expand=True)
    pretrial[["conviction_article_bxd", "conviction_section_bxd"]] = \
                pretrial.top_arraign_article_section.str.split(".",
                                                               n=1,
                                                               expand=True)

    # Pick which bail type was made (cash, credit, bond, none)
    # and record the bail amount. if no bail was made, the amount ins NaN
    print("[Pretrial Release] - Cleaning bail values")
    cash_ser = pretrial[pretrial.bail_made_indicator == "cash"] \
        .first_bail_set_cash
    credit_ser = pretrial[pretrial.bail_made_indicator == "credit"] \
        .first_bail_set_credit
    bond_ser = pretrial[pretrial.bail_made_indicator == "bond"] \
        .first_insurance_company_bail_bond
    null_ser = pretrial[pretrial.bail_made_indicator.isnull()] \
        .bail_made_indicator
    bail_amount = pd.concat([cash_ser, credit_ser, bond_ser, null_ser]) \
        .rename("bail_made_amount_bxd")
    pretrial = pretrial.join(bail_amount)
    del cash_ser
    del credit_ser
    del bond_ser
    del bail_amount    
    
    # Dollar bail flag as boolean
    pretrial['dollar_bail_bxd'] = False
    pretrial.loc[(pretrial.first_bail_set_cash ==1.0),
             'dollar_bail_bxd'] = True
    
     # Prior and pending arrest roll up. 
    priors = [col for col in pretrial.columns if col.startswith("prior")]
    pending = [col for col in pretrial.columns if col.startswith("pend_")]
    
    print("[Pretrial Release] - Summing priors and pending arrest")
    priors = [col for col in pretrial.columns if col.startswith("prior")]
    pending = [col for col in pretrial.columns if col.startswith("pend_")]
    
    print("[Pretrial Release] - Summing priors and pending arrest")
    pretrial["priors_sum_bxd"] = pretrial[priors].sum(axis=1)
    pretrial["pending_arrest_sum_bxd"] = pretrial[pending].sum(axis=1)
    
    print("[Pretrial Release] - Writing data to csv")
    
    ########### write to csv ######################
    pretrial.to_csv("pretrial.csv", encoding='utf-8')
    
    print("[Pretrial Release] - Saving to s3 {}" \
          .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
    ########### Upload to S3 ######################
    
#     tgt_bucket = 'bxdgoogletransformed'
#     tgt_csv = 'pretrial'
#     s3 = boto3.resource('s3')
    
#     f = open(tgt_csv+'.csv', 'rb')
#     try:
#         s3.Bucket(tgt_bucket).put_object(
#                     Key='extract_'+today_str+'/'+tgt_csv+'.csv',
#                     ServerSideEncryption='aws:kms',
#                     StorageClass='STANDARD_IA',
#                     Body=f)
#     except:
#         print("[Pretrial Release] - s3 resource error")
        
#     print("[Pretrial Release] - Load to redshift")

#     ########### load to redshift ######################
#     # HIDE THE CRED STRING BEFORE GITHUB!!!!!
#     cred_string="<!!see tabushextracts/scripting for credentials!!>"

#     trunc_table = "TRUNCATE TABLE google.pretrial; "
#     copy_table = "COPY google.pretrial FROM " 
#     s3_schema = "'s3://bxdgoogletransformed/"
#     path_table = "extract_{}/pretrial.csv' credentials {} " \
#         .format(today_str,cred_string)
#     options_table = "CSV IGNOREHEADER 1;"
#     table_load = trunc_table+copy_table+s3_schema+path_table+options_table


#     # HIDE THE LOGIN BEFORE GITHUB!!!!!
#     conn = None
#     try:
#         print("[Pretrial Release] - open redshift connection {}" \
#              .format(time.strftime("%Y-%m-%d %H:%M:%S")))
#         conn = psycopg2.connect(
#                       dbname='dev',
#                       host='<!!see tabushextracts/scripting for credentials!!>',
#                       port ='5439',
#                       user='xxxx', 
#                       password='xxxx'
#                      )
#         cur = conn.cursor()
#         print("[Pretrial Release] - execute copy from s3 {}" \
#              .format(time.strftime("%Y-%m-%d %H:%M:%S")))
#         cur.execute(table_load)
#         conn.commit()
#         cur.close()
#         print("[Pretrial Release] - close redshift connection {}" \
#              .format(time.strftime("%Y-%m-%d %H:%M:%S")))
#     except psycopg2.DatabaseError as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()


    print("[Pretrial Release] - Done {}" \
      .format(time.strftime("%Y-%m-%d %H:%M:%S")))

