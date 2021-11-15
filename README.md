# OCA  Data

A collection of files that explores the OCA STAT Act data set from the New York State unified court system. 
The state produces this data set each month with new charge data and updates old data from previous months as
the state resolves more cases. More infomation can be found at the [NYS Courts site](https://ww2.nycourts.gov/oca-stat-act-31371).

Additionally, the pretrial release data is contained here. More information about pretrial data can be found at the [NYS courts site](https://ww2.nycourts.gov/pretrial-release-data-33136)

This dataset is a complete set of all criminal arraignments in the State of New York. 

## Thesis app

This is a folder that contains the shiny app for CUNY MSDS Capstone work Fall 2021. 

### `app.R`

The working shiny app file. This file uses the `pretrial.csv` data file. 

### `thesis_eda.R` 

The development file for the app mentioned above. 

## `pretrial.csv`

The data file for the thesis app regarding bail setting practices in NYS.

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

## `pretrial_standalone_dev.ipynb`

Notebook for development of the `pretrial_standalone.py` file. Comments and ec2 instance tested contained within the markdown cells. 

### `utils.py`

This is a utility file that houses helper functions for ETL. It is not meant for standalone use. 

## pretrial_sql_create

Text file to create the necessary DB table. Date types formatted for each column. 

## `OCA_last_modified.txt`

Depreciated. 

