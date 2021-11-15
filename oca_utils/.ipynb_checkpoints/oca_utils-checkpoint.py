import pandas as pd
import numpy as np
import requests

####################### Utility File #######################

# Helper functions and long line of text cleaning are stored here
# See `OCA_scraper.py` for implementation


# Function to determine if new data is present on OCA STAT site.
# Adds last modified date to a list and stores the list for 
# future use. 

def is_downloadable(link_url):
    """
    Does the url contain a recent, downloadable resource
    """
    h = requests.head(link_url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    h.close()
    if 'text' in content_type.lower():
        print("[OCA STAT] - URL error; no text")
        return False
    if 'html' in content_type.lower():
        print("[OCA STAT] - URL error; no html content type")
        return False
    
    return True

################### Remove Accents ##########################

def remove_accents(row):
    return unicode(row, "utf-8")

#################### Make Felony Categories ###################

def make_felonies(row):
    if "120" in row:
        return "assault felony"
    if "125" in row:
        return "murder felony"
    if "130" in row:
        return "sexual assault felony"
    if "135" in row:
        return "kidnapping felony"
    if "140" in row:
        return "burglary felony"
    if "150" in row:
        return "arson felony"
    if "160" in row:
        return "robbery felony"
    if "200" in row:
        return "drug felony"
    if "220" in row:
        return "drug felony"
    if "221" in row:
        return "drug felony"
    else: return row

def make_violations(row):
    if "511" in row:
        return "all 511s"
    else: return row


################# Text Clean Up: Arresting Agency ###############

def make_clean_precincts(oca_data):
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nycpd pct", "nypd")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nycpd", "nypd")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "new york city police department","nypd")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "ny state police", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "new york state police,", "nysp ")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "new york state police", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "new york state police -", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nysp -", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nysp,", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd - housing", "nypd housing")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nysp  - troop f", "nysp troop f")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "metropolitan transportation authority","mta")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "department", "dept")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "dept.", "dept ")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "state police,", "nysp")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "state police-", "nysp ")
    oca_data.arresting_agency = oca_data.arresting_agency.str.rstrip()
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd 0075", "nypd 075")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 10$", "nypd 010")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd 12024424", "nypd 120")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd 19878", "nypd 198")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 5$", "nypd 005")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 6$", "nypd 006")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 72$", "nypd 072")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 76$", "nypd 076")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "^nypd 78$", "nypd 078")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd psa7", "nypd psa 7")
    oca_data.arresting_agency = oca_data.arresting_agency.str.replace(
        "nypd police service area", "nypd")
    
    return oca_data