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
    def __init__(self, url, keeptags=False):
        self.url = url
        self._keeptags = keeptags
        self.soup = self.soupify()
        self.parse_tables()
         
    def soupify(self):
        """ Parse URL. """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

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
             
