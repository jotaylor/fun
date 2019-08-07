#! /usr/bin/env python

from HTMLTableParser import HTMLTableParser
from datetime import datetime

def parse_bwayleague(url="https://www.broadwayleague.com/research/grosses-broadway-nyc"):
    H = HTMLTableParser(url, keeptags=True)
    assert len(H.tables) == 1, "API of URL changed, expected one table, got {}".format(len(H.tables))
    df = H.tables[0]
    for colname in df.columns:
        if colname == "Show":
            col = df[colname]
            get_link_df(col)
            continue
        else:
            col = [row.get_text() for row in df[colname]]
            df[colname] = col
        
        if colname in ["#Perf", "#Prev"]:
            df[colname] = df[colname].astype(int)
        elif colname in ["% Cap", "GG%GP"]:
            df[colname] = removechar(col, "%")
            df[colname] = df[colname].astype(float)
            df[colname] = df[colname]/100.
        elif colname in ["Attend", "AttendPrev Week"]:
            df[colname] = removechar(col, ",")
            df[colname] = df[colname].astype(int)
        elif colname in ["Grosses", "GrossesPrev Week"]:
            df[colname] = removechar(col, "$")
            df[colname] = df[colname].astype(int)
        #elif colname in ["Theatre", "Type"]:
        elif colname == "Week End":
            df[colname] = [datetime.strptime(row, "%m/%d/%Y") for row in df[colname]]
    return df
        
def removechar(col, char):
    stripcol = [row.replace(char, "") for row in col]
    return stripcol

def get_link(col):
    hyperlink = [row.find("a") for row in col]
    href = ["https://www.broadwayleague.com"+row["href"] for row in hyperlink]
    



