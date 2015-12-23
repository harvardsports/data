# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 12:23:08 2015

@author: carlos
"""

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import json

def url(year, country="England"):
    if country == "England":
        var = "_Premier_League"
    elif country =="Spain":
        var = "_La_Liga"
    elif country =="Germany":
        var = "_Bundesliga"
    elif country =="France":
        var = "_Ligue_1"
    elif country =="Italy":
        var = "_Serie_A"
    elif country =="Portugal":
        var = "_Primeira_Liga"
    else:
        raise ValueError('Country Not Found/Implemented')
    if year != 1999:
        return "https://en.wikipedia.org/wiki/"+str(year)+"–"+str(year+1)[2:]+var
    else:
        return "https://en.wikipedia.org/wiki/"+str(year)+"–"+str(year+1)+var
        
def scrape(url, verbose=False, nice = True):
    if verbose:
        print url
    if nice:
        time.sleep(1)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    if len(soup.text.split('Wikipedia does not have an article with this exact name')) == 2:
        print "Article at this link:",url,"doesn't exist"
        return None
    for table in soup.find_all("table", attrs={"class": "wikitable"}):
        try:
            a = table.find_all("tr")[0].find_all('th')[0].get_text()
        except:
            pass
        else:
            if a in ["Pos", 'P']:
                return scrapeTable(table)
    #raise ValueError('Table not Found')
    print "Table Not Found, trying method 2", url
    return scrape_take_2(soup)

def scrape_take_2(soup):
    for i, t in enumerate(soup.find_all('table')):
        try:
            a = t.find_all("tr")[0].find_all('th')[0].get_text()
            b = t.find_all("tr")[0].find_all('th')[1].get_text()
        except:
            pass
        else:
            if a in ['Position', 'P'] and b == 'Club':
                print "Found"
                return scrapeTable(t)
    print "Not Found"
    return None
    
def scrapeTable(table):
    for superscript in table.find_all("sup"):
        superscript.decompose()
    body =  [[entry.get_text() for entry in row.find_all("td")] for row in table.find_all("tr")[1:] if len(row.find_all("td"))>1]
    head =  [[entry.get_text() for entry in table.find_all("tr")[0].find_all("th")]]
    return head+body

# Set verbose to print out each link scraping and nice waits 1 second between requests
# like wikipedia robots.txt asks

verb = False
nice = True


# Set years and leagues
years = range(1990,2016)
leagues = {'e' : "England",
           'g' : "Germany",
           'p' : "Portugal",
           'f' : "France",
           'i' : "Italy",
           's' : "Spain"}
           
print "Using verbose:",verb
print "Using nice:",nice  
           
#data = {k+"pl" : {year : scrape(url(year, v), verbose = verb, nice = nice) for year in years} for k, v in leagues.iteritems()}
data = {v+"_PL" : {year : scrape(url(year, v), verbose = verb, nice = nice) for year in years} for k, v in leagues.iteritems()}

# Export each league to a JSON
for k, v in data.iteritems():
    with open(k+'_tables.json', 'w') as fp:
        json.dump(v, fp)
