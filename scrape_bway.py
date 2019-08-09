#! /usr/bin/env python

from HTMLTableParser import HTMLTableParser
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

BWAY_LEAGUE = "https://www.broadwayleague.com/research/grosses-broadway-nyc"

class BwayData:
    """
    A way to handle the data from Broadway League statistics.
    For now the only attribute is data, but more will be added.

    Args:
        df (:obj:`pandas.DataFrame`): dataframe containing show statistics.
    """
    def __init__(self, df):
        self.data = df

    @classmethod
    def from_url(cls, url=BWAY_LEAGUE):
        """
        Instantiate the class by parsing the data directly from the
        Broadway League website. All modifications to HTML data are done
        in place.

        Args: 
            url (str): URL to parse.
        """
        H = HTMLTableParser(url, keeptags=True)
        assert len(H.tables) == 1, "API of URL changed, expected one table, got {}".format(len(H.tables))
        df = H.tables[0]
        for colname in df.columns:
            if colname == "Show":
                col = [row.get_text() for row in df[colname]]
                df[colname] = col
    # Not sure how to do this yet
    #            col = df[colname]
    #            get_link_df(col)
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
                col = removechar(col, "$")
                df[colname] = col
                df[colname] = removechar(col, ",")
                df[colname] = df[colname].astype(int)
            #elif colname in ["Theatre", "Type"]:
            elif colname == "Week End":
                df[colname] = [datetime.strptime(row, "%m/%d/%Y") for row in df[colname]]

        colmapping = {"#Perf": "nshows",
                      "#Prev": "nprevs",
                      "% Cap": "capacity",
                      "Attend": "nsold",
                      "AttendPrev Week": "nsold_previous",
                      "GG%GP": "perc_gp",
                      "Grosses": "gross",
                      "GrossesPrev Week": "gross_previous",
                      "Show": "show",
                      "Theatre": "theater",
                      "Type": "showtype",
                      "Week End": "enddate"}
        df2 = df.rename(columns=colmapping)
        
        df2["totalshows"] = df2["nshows"] + df2["nprevs"]
        return cls(df2)

    def plot_grosses(self):
        """
        Plot the gross and scaled gross values (gross per show) as a
        function of show, for one given week.
        """
        fig = go.Figure()
        trace0 = go.Scatter(x=self.data["show"], y=self.data["gross"],
                            mode="markers+lines",
                            line=dict(color="royalblue", width=4),
                            marker=dict(size=12),
                            name="Gross")
        factor = np.average(self.data["gross"])/np.average(self.data["totalshows"])
        trace1 = go.Scatter(x=self.data["show"], 
                            y=self.data["gross"]/self.data["totalshows"],
                            mode="markers+lines",
                            line=dict(color="mediumorchid", width=4),
                            marker=dict(size=12),
                            name="Gross/Show (Scaled)")
        data = [trace0, trace1]
    
        fontd = {"family":"Courier New, monospace",
                 "size":18,
                 "color":"#7f7f7f"}
        layout = go.Layout(title="Gross",
                           xaxis_title="Show",
                           yaxis_title="Gross [$]")
    #                       xaxis=dict(text="Show", font=dict(),
    #                       yaxis=dict(text="Gross [$]", font=fontd))
        
        fig = go.Figure(data=data, layout=layout)
        fig.write_html("grosses.html", auto_open=True)

#-----------------------------------------------------------------------------#        
def removechar(arr, char):
    """ Remove a string character from each element in an array. """
    striparr = [row.replace(char, "") for row in arr]
    return striparr

def get_link(arr):
    """ Get URL link for each BSD tag object in an array. """
    hyperlink = [row.find("a") for row in arr]
    href = ["https://www.broadwayleague.com"+row["href"] for row in hyperlink]
    
