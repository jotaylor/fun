#! /usr/bin/env python

from bs4 import BeautifulSoup
import requests
import pandas as pd
from collections import defaultdict

class HTMLTableParser:
    """
    A simple and generic way to parse HTML Tables using BeautifulSoup.
    Tables are returned as list of Pandas dataframes.

    Args:
        url (str): URL to parse.
        keeptags (Bool): If True, raw tags from table will be stored in the
            dataframe. This is useful if there is metainformation of interest
            e.g. links.
    """
    def __init__(self, soup, keeptags=False):
        self._keeptags = keeptags
        self.soup = soup
        self.parse_tables()
   
    @classmethod
    def from_url(cls, url, keeptags=False):
        soup = soupify(url=url)
        c = cls(soup, keeptags)
        c.url = url
        return c

    @classmethod
    def from_html(cls, html, keeptags=False):
        soup = soupify(html=html)
        c = cls(soup, keeptags)
        c.html = html
        return c
         
    def parse_tables(self):
        """ Parse all HTML tables in the URL, storing header and row information. """
        self.tables = []
        # Get all tables
        tables = self.soup.find_all("table")
        for table in tables:
            data = defaultdict(list)
            # Get all rows from the table
            rows = table.find_all("tr")
            colnames = None
            for i in range(len(rows)):
                # If not already done, see if there is a table header 
                # which contains column names
                if colnames is None:
                    header = rows[i].find_all("th")
                    colnames = [col.get_text() for col in header if len(header) > 0]
                cols = rows[i].find_all("td")
                # If the table row data is empty, it's likely the table heder, so skip.
                if len(cols) != 0:
                    if len(cols) != len(colnames):
                        print("WARNING!")
                        print("Number of columns in row {}, {}, does not match number of column names, {}".format(i, len(cols), len(colnames)))
                        print("Skipping row for now...")
                        continue
                    # Storing data in a dictionary is the only way to retain bs4 tag
                    # objects; np.arrays cannot handle them.
                    for j in range(len(cols)):
                        if self._keeptags is True:
                            coldata = cols[j]
                        else:
                            coldata = cols[j].get_text()
                        data[colnames[j]].append(coldata)
            # Insert the table data in a dataframe and append to a list of tables.
            df = pd.DataFrame(data=data)
            self.tables.append(df)
             
def soupify(url=None, html=None, text=None, parser="html.parser"):
    """ 
    Parse URL. 
    
    Args:
        url (str): URL to parse.
        html (str): Downloaded HTML file to parse.
        text (str): Raw string text to parse.
        parser (str): BeautifulSoup parser type.

    Returns:
        soup (bs4.BeautifulSoup): BeautifulSoup object containing HTML info.
    """

    if url is not None:
        response = requests.get(url)
        primordial = response.text
    elif html is not None:
        with open(html) as f:
            primordial = f.read()
    elif text is not None:
        primordial = text
    soup = BeautifulSoup(primordial, "html.parser")
   
    return soup
