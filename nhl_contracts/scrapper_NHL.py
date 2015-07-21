from bs4 import BeautifulSoup
import requests
import os
import sys
import csv

def getYears():
    return range(2008,2016)

def getTeams():
    url = "http://www.spotrac.com/"
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    soup_ = soup.find("li", {"class": "cat-nhl "})
    table = soup_.find_all("div", {"class": "subnav-posts"})[0]
    teams = [team['href'] for team in table.find_all('a')]
    return teams

def getData(team, year):
    url = team+"cap/"+str(int(year))+"/"
    #print url
    try:
        r = requests.get(url)
    except:
        "Error with: ", url
    else:
        data = r.text
        soup = BeautifulSoup(data, 'html5lib')
        soup_ = soup.find_all("tbody")[0]
        players = []
        for player in soup_.find_all("tr"):
            temp = [year, team.split('/')[4].replace ("-", " ").title()]
            for i, data in enumerate(player.find_all("td")):
                try:
                    temp = temp + data.find('a').contents
                except AttributeError:
                    try:
                        temp = temp + data.next.contents
                    except:
                        temp.append(data.next)
            players.append(temp)
        return players
              
def scrapper():
    years = getYears()
    teams = getTeams()
    data = []
    for year in years:
        for team in teams:
            data = data + getData(team, year)
    return data

def csvwriter(directory, filename):
    data = scrapper()
    with open(os.path.join(directory + "\\"+filename), "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['Year', 'Team', 'Player', 'Position', 'Age', 'Base_Salary', 'Signing_Bonus', 'Performance_Bonus', 'Total_Salary', 'Cap_Figure'])
        for datapoint in data:
            writer.writerow(datapoint)

def fileExists(directory, filename):
    return os.path.isfile(directory+"\\"+filename)

def main(*args):
    try:
        args[1]
    except IndexError:
        update = False
    else:
        if (args[1] == "--update"):
            update = True
        else:
            update = False
    directory = os.path.dirname(os.path.abspath(__file__))
    filename = "nhl_contracts.csv"
    if  ((not fileExists(directory, filename)) | update == True):
        csvwriter(directory, filename)
    else:
        print "File already exists:\nRun with --update flag to update file"
    
if __name__ == '__main__':
    main(*sys.argv)
