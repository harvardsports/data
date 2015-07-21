from bs4 import BeautifulSoup
import requests
import os
import sys
import csv

def getRownames(league):
    if league == "nfl":
        return ['Base_Salary', 'Signing_Bonus', 'Roster_Bonus', 'Option_Bonus', 'Workout_Bonus', 'Restructure_Bonus', 'Miscellaneous', 'Dead_Cap', 'Cap_Hit', 'Cap_Percentage']
    elif league == "nba":
        return ['Signed Using', 'Base_Salary', 'Signing_Bonus', 'Trade_Kicker', 'Likely_Incentives', 'Unlikely_Incentives', 'Dead_Cap', 'Cap_Figure', 'Cap_Percentage']
    elif league == "mlb":
        return ['Signed Using', 'Base_Salary', 'Signing_Bonus', 'Trade_Kicker', 'Likely_Incentives', 'Unlikely_Incentives', 'Dead_Cap', 'Cap_Figure', 'Cap_Percentage']
    elif league == "nhl":
        return ['Age', 'Base_Salary', 'Signing_Bonus', 'Performance_Bonus', 'Total_Salary', '', 'Cap_Figure']
    # Currently Spotrac is very buggy with MLS
    #elif league == "mls":
    #    return ['Signed Using', 'Base_Salary', 'Signing_Bonus', 'Trade_Kicker', 'Likely_Incentives', 'Unlikely_Incentives', 'Dead_Cap', 'Cap_Figure', 'Cap_Percentage']
    else:
        print "Please input a VALID league to scrape NFL/NBA/MLB/NHL"
        sys.exit(2)
    
def getYears():
    return range(2004,2016)

def getTeams(league):
    url = "http://www.spotrac.com/"
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    soup_ = soup.find("li", {"class": "cat-"+league+" "})
    table = soup_.find_all("div", {"class": "subnav-posts"})[0]
    teams = [team['href'] for team in table.find_all('a')]
    return teams

def getData(team, year, league):
    # Problem with SpoTrac MLB contracts, can't be found with this format:
    # http://www.spotrac.com/mlb/arizona-diamondbacks/cap/2011/.  However they can be found incorrectly as follows
    # http://www.spotrac.com/nba/arizona-diamondbacks/cap/2011/    
    url = team+"cap/"+str(int(year))+"/"
    if league == "mlb":
        url = url.replace("mlb", "nba")
    print url
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
                    temp.append(data.find('a').contents.pop().encode("latin-1"))
                except AttributeError:
                    try:
                        if data.next.contents == []:
                            data.next.contents = ['-']
                        temp = temp + data.next.contents
                    except:
                        temp.append(data.next)
            players.append(temp)
        return players
              
def scrapper(league):
    years = getYears()
    teams = getTeams(league)
    data = []
    for year in years:
        for team in teams:
            data = data + getData(team, year, league)
    return data

def csvwriter(directory, filename, rownames, league):
    data = scrapper(league)
    with open(os.path.join(directory + "\\"+filename), "wb") as f:
        writer = csv.writer(f)
        writer.writerow(['Year', 'Team', 'Player', 'Position']+rownames)
        for datapoint in data:
            writer.writerow(datapoint)

def fileExists(directory, filename):
    return os.path.isfile(directory+"\\"+filename)

def main(*args):
    try:
        league = args[1].lower()
        rownames = getRownames(league)
    except IndexError:
        print "Please input a league to scrape NFL/NBA/MLB/NHL"
        sys.exit(1)
    try:
        args[2]
    except IndexError:
        update = False
    else:
        if (args[2] == "--update"):
            update = True
        else:
            update = False
    directory = os.path.dirname(os.path.abspath(__file__))
    filename = league + "_contracts.csv"
    if  ((not fileExists(directory, filename)) | update == True):
        csvwriter(directory, filename, rownames, league)
    else:
        print "File \""+filename+"\" already exists:\nRun with --update flag to update file"
    
if __name__ == '__main__':
    main(*sys.argv)
