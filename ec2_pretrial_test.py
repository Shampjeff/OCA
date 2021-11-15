import zipfile
import pandas as pd
import timeit
from zipfile import ZipFile
from StringIO import StringIO
import urllib2
import fnmatch
import os
import json

start_time = timeit.default_timer()

link_url= "http://www.nycourts.gov/"
link_subpath= "LegacyPDFS/court-research/"
link_file= "PretrialReleaseDataExtractWeb2020.zip"
link_url= link_url+link_subpath+link_file

r = urllib2.urlopen(link_url).read()
file_ex = ZipFile(StringIO(r))
file_ex.extractall()
pattern = "*-revised.csv"

for root, dirs, files in os.walk(os.getcwd(),):
    for filename in fnmatch.filter(files, pattern):
        pretrial_csv = file_ex.open(filename)
        pretrial = pd.read_csv(pretrial_csv)

elapsed = timeit.default_timer() - start_time
print("zip extract completed in: ",elapsed)

start_time = timeit.default_timer()

pretrial.columns = pretrial.columns.str.lower()
date_cols = [col for col in pretrial.columns if col.endswith('_date')]
not_date_type = ["first_bench_warrant_date","rearrest_date"]
for col in date_cols:
    if col in not_date_type:
        pretrial[col] = pd.to_datetime(pretrial[col],format="%b-%y")
    pretrial[col] = pd.to_datetime(pretrial[col],errors='coerce')
    
elapsed = timeit.default_timer() - start_time
print("date format completed in: ",elapsed)


start_time = timeit.default_timer()

for col in pretrial:
    if pretrial[col].dtype == "O":
        pretrial[col] = pretrial[col].str.lower()

elapsed = timeit.default_timer() - start_time
print("case to lower compelte in: " e, lapsed)

