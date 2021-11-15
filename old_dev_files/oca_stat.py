import requests
from contextlib import closing
import csv
import pandas as pd
import numpy as np
import time
import boto3
import botocore
import string
from oca_utils.oca_utils import *

################################### OCA-STAT SCRAPER ########################

# Script to pull the OCA site for new data, and writes that to csv
# Some file and "error" handling to check if files have moved or changed
# on the NYS court site. 

today_str = time.strftime("%Y-%m-%d")

link_url= "https://www.nycourts.gov/"
link_path = "LegacyPDFS/court-research/OCA-STAT-Act.csv"
link_url= link_url+link_path

try:
    is_downloadable(link_url)
    print("[OCA STAT] - Vaild URL. Reading data.")
except requests.ConnectionError as exception:
    print("[OCA STAT] - Not a valid URL.")
    
data_list = []
print("[OCA STAT] - Connection open {}." \
      .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
data_list = []
with closing(requests.get(link_url, stream=True)) as r:
    f = (line.decode('utf-8', 'ignore') for line in r.iter_lines())
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        data_list.append(row)

print("[OCA STAT] - Connection closed {}." \
      .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
      
oca_data = pd.DataFrame(data_list[1:], columns=data_list[0])
oca_data.dropna(axis = 0, how = 'any', inplace=True)
        
###################### CLEAN AND ORGANIZE #######################


try:
    isinstance(oca_data, pd.DataFrame)
except: 
    print("[OCA STAT] - No dataframe present")
else:
    print("[OCA STAT] - Cleaning Data")
    
    oca_data.columns = oca_data.columns.str.replace(" ", "_"). \
            str.replace(".", "_")
    oca_data.columns = oca_data.columns.str.lower()
    oca_data.arraign_year = pd.to_numeric(oca_data.arraign_year, 
                                      errors='coerce') \
                            .fillna(0).astype(np.int64)
    oca_data.arraign_month = pd.to_numeric(oca_data.arraign_month, 
                                      errors='coerce') \
                            .fillna(0).astype(np.int64)
    oca_data.arrest_age = pd.to_numeric(oca_data.arrest_age, 
                                      errors='coerce')
    oca_data.fines_imposed = pd.to_numeric(oca_data.fines_imposed, 
                                      errors='coerce')
    oca_data.fees_imposed = pd.to_numeric(oca_data.fees_imposed, 
                                      errors='coerce')
    oca_data.surcharges_imposed = pd.to_numeric(oca_data.surcharges_imposed, 
                                      errors='coerce')
    oca_data = oca_data.applymap(lambda x:x.lower() if type(x) == str else x)
    oca_data.article_section = oca_data.article_section.str.rstrip(".")
    oca_data.article_section = oca_data.article_section.str.replace("\.\.", ".")
    oca_data.drop("row_#",axis=1, inplace=True)
    oca_data[["article", "section"]] = \
            oca_data.article_section.str.split(".",n=1,expand=True)
    
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
    
    ########### remove punctuation and accent varchars ###############
    for col in oca_data:
        if oca_data[col].dtype == "O":
            oca_data[col] = oca_data[col].str \
                .replace('[{}]'.format(string.punctuation),' ')
            
    oca_data.top_charge_at_arraignment = \
        oca_data.top_charge_at_arraignment.apply(lambda x: remove_accents(x))
    
    print("[OCA STAT] - Writing data to csv")
    
    ########### write to csv ######################
    oca_data.to_csv("oca_stat.csv", encoding='utf-8')
    
    print("[OCA STAT] - Saving to s3 {}" \
          .format(time.strftime("%Y-%m-%d:%H:%M:%S")))
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