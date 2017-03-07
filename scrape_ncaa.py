#! /usr/bin/env python

'''
This
'''

import matplotlib.pyplot as pl
pl.style.use("ggplot")
import numpy as np
from bs4 import BeautifulSoup
import requests

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------# 

def parse_espn():
    url = "http://www.espn.com/mens-college-basketball/rankings"
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    
    espn_dict = {"ap": {},
                 "usa": {} } 
    h1 = soup.find("h1")
    header = h1.get_text()
    words = header.split()
    season = words[0]
    if "Preseason" in header:
        final_week = "1"
    else:
        final_week = words[words.index("Week") + 1]
    
    for week in np.arange(1, int(final_week)+1)[::-1]:
        espn_dict["ap"][week] = {}
        espn_dict["usa"][week] = {}
        if week != final_week:
            url = "http://www.espn.com/mens-college-basketball/rankings/_/year/{0}/week/{1}/".format(season, week)
            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)
        all_tables = soup.find_all("table")
        for table in all_tables:
            rows = table.find_all("tr")
            for i in range(len(rows)):
                cols = rows[i].find_all("td")
                if i == 0:
                    polltype = cols[0].get_text()
                    if polltype == "AP Top 25":
                        poll = "ap"
                    elif polltype == "USA Today Coaches Poll":
                        poll = "usa"
                elif i == 1:
                    continue
                else:
                    for ind, key in enumerate(["rank","team","record"]):
                        if not key in espn_dict[poll][week].keys():
                            espn_dict[poll][week][key] = []
                        colval = cols[ind].get_text()
                        keyval = colval.split("(")[0].strip()
                        espn_dict[poll][week][key].append(keyval)

    return espn_dict, season

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------# 

def plot_rank_v_week(team_dict, season, save):
    for team in team_dict["ap"].keys():
        fig, ax = pl.subplots(figsize=(9, 6))
        ap_ranks = team_dict["ap"][team]
        ap_weeks = range(len(ap_ranks))
        ax.plot(ap_weeks, ap_ranks, "o-", color="royalblue", label="AP")
        try:
            usa_ranks = team_dict["usa"][team]
            usa_weeks = range(len(usa_ranks))
        except KeyError:
            pass    
        else:
            ax.plot(usa_weeks, usa_ranks, "o-", color="mediumturquoise", label="USA")
        
        ax.set_ylim(26, -1)
        ax.set_xlim(-1, 18)
        ax.legend(loc="best")
        ax.set_xlabel("Week")
        ax.set_ylabel("Rank")
        ax.set_title("{0} {1} Rankings".format(season, team))
        if save:
            figname = "{0}_rank_v_time.png".format(team)
            fig.savefig(figname, bbox_inches="tight", dpi=200)
            print("Saved {0}".format(figname))
        else:
            fig.show()
            this = input("Press enter to continue")

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------# 

def compile_team_info(espn_dict):
    team_dict = {}
    for poll in espn_dict.keys():
        team_dict[poll] = {}
        for week in espn_dict[poll].keys():
            teams = espn_dict[poll][week]["team"]
            ranks = espn_dict[poll][week]["rank"]
            for i in range(len(teams)):
                if teams[i] not in team_dict[poll].keys():
                    if int(week) == 1:
                        team_dict[poll][teams[i]] = [ranks[i]]
                    else:
                        team_dict[poll][teams[i]] = [30 for x in range(int(week)-1)]
                        team_dict[poll][teams[i]].append(ranks[i])
                else:
                    team_dict[poll][teams[i]].append(ranks[i])
            for team in team_dict[poll].keys():
                if len(team_dict[poll][team]) != week:
                    team_dict[poll][team].append(30)

    return team_dict                    

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    espn_dict, season = parse_espn()
    team_dict = compile_team_info(espn_dict)
    plot_rank_v_week(team_dict, season, True)
