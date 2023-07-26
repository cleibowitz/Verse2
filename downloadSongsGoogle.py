"""
Chase Leibowitz
M&TSI 2023
7/21/23
download data from google spreadsheet using API to do stuff with it
"""

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe



# Set up credentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\chase\Downloads\sixth-hawk-393504-f8baa14e8c72.json', scope)
client = gspread.authorize(creds)

# open spreadsheet
spreadsheet = client.open('userSongs')

# figure out where to start working -- index of where to start working in the spreadsheet -- add somethign later to start after other stuff
worksheet = spreadsheet.get_worksheet(0)

existing_data = worksheet.get_all_values()
len_data = len(existing_data)

# download data from spreadsheet and save as df
df = get_as_dataframe(worksheet, evaluate_formulas=True, skiprows=0)


# delete all of the empty rows and columns that get imported
df = df.dropna(how='all')
df = df.dropna(axis=1, how='all')

#print(df)


# print songs (cleaned up to look good)
"""print("Downloaded songs from cloud")
clean_df = df[["Track Name", "Artist"]]
print(clean_df)"""

