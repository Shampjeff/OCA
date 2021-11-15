# OCA STAT Act Data

A collection of files that explores the OCA STAT Act data set from the New York State unified court system. 
The state produces this data set each month with new charge data and updates old data from previous months as
the state resolves more cases. More infomation can be found at the [NYS Courts site](https://ww2.nycourts.gov/oca-stat-act-31371).

This dataset is a complete set of all criminal arraignments in the State of New York. 

The primary function of this repository is a collection of files to extract, transform, and load this data into the BxD database.

## `oca_scaper_dev.ipynb`

This is a notebook that provides a working file to experimenting with new methods to clean and load the data. 
Not all functionality is currently in use/meaningful. This is the sandbox for determining what we will use in other files. There is a `_27` version as well, this is writen in python 2.7.x 

## `oca_stat_production_copy.py`

This is the main file for extracting the data from the NYS Courts site. This file checks for new data on the OCA site
and extracts new data if available. The file then cleans and organizes the data in format that BxD would like. The data is a then uploaded to ec2, s3, and BxD DB. 

## `oca_stat_standalone.py`

File for independently scrapping the OCA site for OCA STAT ACT data. This is a backup to the production copy and can be used to troubleshoot issues with the production verison.

## `pretrial_standalone.py`

File for scrapping the pretrial data also from OCA site. This data is released every six months and contains activities relating to defendents pretrial. It also contains all the court data as well prior arrests and convictions. 

The file scrapes the data and loads a csv file to s3 and the BxD DB. 

## `pretrial_standalone_dev.ipynb`

Notebook for development of the `pretrial_standalone.py` file. Comments and ec2 instance tested contained within the markdown cells. 

### `utils.py`

This is a utility file that houses helper functions for ETL. It is not meant for standalone use. 

## pretrial_sql_create

Text file to create the necessary DB table. Date types formatted for each column. 

## `OCA_last_modified.txt`

Depreciated. 

## `Rmd` files

A couple of R markdown files for early EDA and text clean up explorations. For ease of use, we switched from R to Python for this project. 
