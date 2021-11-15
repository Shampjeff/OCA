import requests
import pandas as pd
import io
import pickle
import os
import time
import boto3
import botocore
from oca_utils.oca_utils import *

################################### OCA-STAT SCRAPER ########################

# Script to pull the OCA site for new data, and writes that to csv
# Some file and "error" handling to check if files have moved or changed
# on the NYS court site. 
# This script stores a list of last modified dates found in the url header.
# Only downloads data if a new last modified date is present. 

today_str = time.strftime("%Y-%m-%d")
#today_str_log = time.strftime("%Y-%m-%d %H:%M:%S")

# if os.path.exists("OCA_last_modified.txt"):
#     fp=open("OCA_last_modified.txt", "r")
#     mod_list = pickle.load(fp)
# else:
mod_list = []
    

link_url= "https://www.nycourts.gov/"
link_path = "LegacyPDFS/court-research/OCA-STAT-Act.csv"
link_url= link_url+link_path

# if is_downloadable(link_url, mod_list):
# print("[OCA STAT] - Checking for data {}" \
#       .format(time.strftime("%Y-%m-%d %H:%M:%S")))
# try:
# print("[OCA STAT] - sending get request")

with requests.get(link_url, stream=True) as r:
    
    last_mod = r.headers['Last-Modified']
    mod_list.append(last_mod)
    print("[OCA STAT] - reading data from site {}" \
          .format(time.strftime("%Y-%m-%d %H:%M:%S")))
    oca_data = pd.read_csv(io.StringIO(r.text))
    r.close()
    print("[OCA STAT] - New data loaded. Done with check {}" \
          .format(time.strftime("%Y-%m-%d %H:%M:%S")))
#else: print("[OCA STAT] - Done with check")




# try:
#     with open("OCA_last_modified.txt", "wb") as fp:
#         pickle.dump(mod_list, fp)
#         print("[OCA STAT] - Saved updated scrape date {}".format(today_str_log))
# except: 
#     print("[OCA STAT] - No last modified date. check for file in directory or `is_downloadable` function") 
        
###################### CLEAN AND ORGANIZE #######################


### Clean data if new rows are present.

try:
    isinstance(oca_data, pd.DataFrame)
except: 
    print("[OCA STAT] - No dataframe present")
else:
    print("[OCA STAT] - Cleaning Data")
    oca_data = oca_data.applymap(lambda x:x.lower() if type(x) == str else x)
    oca_data.columns = oca_data.columns.str.replace(" ", "_").str.replace(".", "_")
    oca_data.columns = oca_data.columns.str.lower()
    oca_data.article_section = oca_data.article_section.str.rstrip(".")
    oca_data.article_section = oca_data.article_section.str.replace("\.\.", ".")
    oca_data.drop("row_#",axis=1, inplace=True)
    oca_data[["article", "section"]] = oca_data.article_section.str.split(".",
                                                                          n=1,
                                                                         expand=True)
    
    # Clean precincts; see `utils.py`
    oca_data = make_clean_precincts(oca_data)
    
    # Make meta categories for crimes we want to track. Based
    # on the article and and weight/severity. see `utils.py`
    # for details on assignment. 
    
    fel_weights = [x for x in oca_data.weight.unique() if "f" in x]
    fel_series = oca_data[oca_data.weight.isin(fel_weights)] \
        .article.apply(lambda x: make_felonies(x))
    vio_series = oca_data[oca_data.law.isin(["vtl"])] \
        .article.apply(lambda x: make_violations(x))
    bxd_category = pd.concat([fel_series, vio_series]) \
        .rename("category_bxd")
    oca_data = oca_data.join(bxd_category)
    
    # Make weapons and sex charges column based on arraignment description.
    # This might not be 100% accurate as subsections are not present in 
    # this data set, so we are basing the exisitance of a weapons/sex charge
    # on if the word (or some facsimile thereof) exists in the arraignment text.
    
    weapons = ("|").join(["wea", "wpn", "wep"])
    oca_data['weapon_charge_bxd'] = False
    oca_data.loc[(oca_data.top_charge_at_arraignment.str.contains(weapons)) &
        (oca_data.weight != "v"), 'weapon_charge_bxd'] = True
    
    sex_charge = ("|").join(["sex", "sx"])
    oca_data["sex_charge_bxd"] = False
    oca_data.loc[oca_data.top_charge_at_arraignment.str.contains(sex_charge),
             "sex_charge_bxd"] = True
    
    oca_data = oca_data.rename(columns={"article":"article_bxd",
                                        "section":"section_bxd"})
    
    print("[OCA STAT] - Writing data to csv")
    
    ########### write to csv ######################
    oca_data.to_csv("oca_stat.csv", encoding='utf-8')
    
    print("[OCA STAT] - Saving to s3 {}" \
          .format(time.strftime("%Y-%m-%d %H:%M:%S")))
    ########### Upload to S3 ######################
    
#     tgt_bucket = 'bxdgoogletransformed'
#     tgt_csv = 'oca_stat'
#     s3 = boto3.resource('s3')
    
#     f = open(tgt_csv+'.csv', 'rb')
#     try:
#         s3.Bucket(tgt_bucket).put_object(
#                     Key='extract_'+today_str+'/'+tgt_csv+'.csv',
#                     ServerSideEncryption='aws:kms',
#                     StorageClass='STANDARD_IA',
#                     Body=f)
#     except:
#         print("[OCA STAT] - s3 resource error")

print("[OCA STAT] - Done {}" \
      .format(time.strftime("%Y-%m-%d %H:%M:%S")))