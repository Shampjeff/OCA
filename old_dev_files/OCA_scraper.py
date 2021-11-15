import requests
import pandas as pd
import io
import pickle
import os
from utils import *

################################### OCA-STAT SCRAPER ########################

# Script to pull the OCA site for new data, and writes that to csv
# Some file and "error" handling to check if files have moved or changed
# on the NYS court site. 
# This script stores a list of last modified dates found in the url header.
# Only downloads data if a new last modified date is present. 

# Future work needed
# 1) Trigger execution of this script on some interval
# 2) Integrate an upload to AWS Redshift


if os.path.exists("OCA_last_modified.txt"):
    with open("OCA_last_modified.txt", "rb") as fp:
        mod_list = pickle.load(fp)
else:
    mod_list = []
    
print("Last modified:", mod_list[-1])

link_url= "https://www.nycourts.gov/"
link_path = "LegacyPDFS/court-research/OCA-STAT-Act.csv"
link_url= link_url+link_path

if is_downloadable(link_url, mod_list):
    print("Downloading new data.")
    r = requests.get(link_url)
    last_mod = r.headers['Last-Modified']
    mod_list.append(last_mod)
    oca_data = pd.read_csv(io.StringIO(r.text))
else: print("No new data present.")

print("Done with download check.")

if mod_list:
    with open("OCA_last_modified.txt", "wb") as fp:
        pickle.dump(mod_list, fp)
        
        
###################### CLEAN AND ORGANIZE #######################

print("Cleaning Data")

### Clean data if new rows are present.

if isinstance(oca_data, pd.DataFrame):
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
        .rename("bxd_category")
    oca_data = oca_data.join(bxd_category)
    
    # Make weapons and sex charges column based on arraignment description.
    # This might not be 100% accurate as subsections are not present in 
    # this data set, so we are basing the exisitance of a weapons/sex charge
    # on if the word (or some facsimile thereof) exists in the arraignment text.
    
    weapons = ("|").join(["wea", "wpn", "wep"])
    oca_data['weapon_charge'] = False
    oca_data.loc[(oca_data.top_charge_at_arraignment.str.contains(weapons)) &
        (oca_data.weight != "v"), 'weapon_charge'] = True
    
    sex_charge = ("|").join(["sex", "sx"])
    oca_data["sex_charge"] = False
    oca_data.loc[oca_data.top_charge_at_arraignment.str.contains(sex_charge),
             "sex_charge"] = True
    
    print("writing data to csv")
    
    ########### write to csv ######################
    oca_data.to_csv("oca_data_clean_final.csv")

