#! /usr/bin/env python

'''
Scrape the ESPN website to get all NCAA Men's Basketball rankings from week 1
to the current week. Produce diagnostic pltos of rankings vs. time.

Usage:
    python scrape_ncaa.py
'''

__author__ = "Jo Taylor"
__date__ = "03-01-2017"
__maintainer__ = "Jo Taylor"
__email__ = "jotaylor@stsci.edu"

import matplotlib.pyplot as pl
pl.style.use("ggplot")
import numpy as np
from bs4 import BeautifulSoup
import requests

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------# 

def parse_espn():
    '''
    Get the HTML source code from ESPN and gather the rankings from the AP
    Top 25 and USA Today Coaches Poll.

    Parameters:
    -----------
        None

    Returns:
    --------
        espn_dict : dictionary
            Dictionary describing rankings as a function of poll.
        season : str
            Year of season of interest.
    '''
    
    # The current rankings should always be at this URL.
    url = "http://www.espn.com/mens-college-basketball/rankings"
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")

    # Initialize dictionary.    
    espn_dict = {"ap": {},
                 "usa": {} } 

    # Get the header of the webpage, which describes the current year (season)
    h1 = soup.find("h1")
    header = h1.get_text()
    words = header.split()
    season = words[0]
    # Preseason = Week 1
    if "Preseason" in header:
        final_week = "1"
    else:
        final_week = words[words.index("Week") + 1]
   
    # Work backwards from the final week to week 1
    for week in np.arange(1, int(final_week)+1)[::-1]:
        espn_dict["ap"][week] = {}
        espn_dict["usa"][week] = {}
        if week != final_week:
            # For all weeks not the one we started at, change the URL
            # and get HTML text
            url = "http://www.espn.com/mens-college-basketball/rankings/_/year/{0}/week/{1}/".format(season, week)
            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)
        
        # Get the HTML tables (there should be 2, one for each poll).
        all_tables = soup.find_all("table")
        for table in all_tables:
            # Get all rows from the table
            rows = table.find_all("tr")
            for i in range(len(rows)):
                cols = rows[i].find_all("td")
                # The first row contains the poll information.
                if i == 0:
                    polltype = cols[0].get_text()
                    if polltype == "AP Top 25":
                        poll = "ap"
                    elif polltype == "USA Today Coaches Poll":
                        poll = "usa"
                # The second row contains the Column names, which we don't want
                elif i == 1:
                    continue
                else:
                    # Get the rank, team, and season record 
                    for ind, key in enumerate(["rank","team","record"]):
                        if not key in espn_dict[poll][week].keys():
                            espn_dict[poll][week][key] = []
                        # Need to do split and strip on result to ensure you
                        # get full team name (e.g. Notre Dame)
                        colval = cols[ind].get_text()
                        keyval = colval.split("(")[0].strip()
                        espn_dict[poll][week][key].append(keyval)

    return espn_dict, season

#-----------------------------------------------------------------------------# 
#-----------------------------------------------------------------------------# 

def plot_rank_v_week(team_dict, season, save):
    '''
    Plot the rank vs. week for each team that is ranked at least once during
    the season.

    Paramaters:
    -----------
        team_dict : dictionary
            Dictionary describing teams as a function of rank.
        season : str
            Year of season of interest.
        save : Bool
            Switch to save figure.

    Returns:
    --------
        None
    '''

    for team in team_dict["ap"].keys():
        fig, ax = pl.subplots(figsize=(9, 6))
        ap_ranks = team_dict["ap"][team]
        ap_weeks = range(len(ap_ranks))
        ax.plot(ap_weeks, ap_ranks, "o-", color="royalblue", label="AP")
        # The AP and USA polls differ sometimes, so check if team is ranked in
        # both polls.
        try:
            usa_ranks = team_dict["usa"][team]
            usa_weeks = range(len(usa_ranks))
        except KeyError:
            pass    
        # If the team is ranked in USA as well, plot both. Otherwise only plot
        # AP poll. 
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
    '''
    Take the output from parse_espn, and create a new dictionary that describes
    ranks as a function of week for each team ranked at least once during the
    season, for each poll. 
    E.g. {"ap": {"indiana": [1,1,1,1,1], "purdue": [25,30,30,30,30],...},
          "usa": ...}
    
    Parameters:
    -----------
        espn_dict : dictionary
            Dictionary describing rankings as a function of poll.
    
    Returns:
    --------
        team_dict : dictionary
            Dictionary describing teams as a function of rank.
    '''
    
    # Initialize dictionary.
    team_dict = {}
    for poll in espn_dict.keys():
        # Create dictionary for each poll (ap vs usa).
        team_dict[poll] = {}

        # Loop over each week in espn_dict and get all teams that were ranked.
        for week in espn_dict[poll].keys():
            teams = espn_dict[poll][week]["team"]
            ranks = espn_dict[poll][week]["rank"]
            
            # Loop over teams that in espn_dict.
            for i in range(len(teams)):
                # If team not ranked, add it to team_dict and fill in previous
                # weeks (if not week 1) with "unranked", which I call rank=30.
                if teams[i] not in team_dict[poll].keys():
                    if int(week) == 1:
                        team_dict[poll][teams[i]] = [ranks[i]]
                    else:
                        team_dict[poll][teams[i]] = [30 for x in range(int(week)-1)]
                        team_dict[poll][teams[i]].append(ranks[i])
                # If team has already been ranked in a previous week, just add 
                # current rank to its rank list.
                else:
                    team_dict[poll][teams[i]].append(ranks[i])

            # Loop over teams already ranked, if they were not ranked during 
            # week, add "unranked (rank=30) to ranks list. 
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
