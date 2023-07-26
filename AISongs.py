"""
Chase Leibowitz
M&TSI 2023
7/21/23

This script takes the user's favorite songs from the cloud from the downloadData script, uploads it to the GPT 3.5 Turbo API,
and then gets a return of similar songs. The script then cleans the data and prints it.
"""

import openai
import requests
from downloadSongsGoogle import df, len_data
import pandas as pd
import webbrowser
import spotipy
from spotipy import SpotifyOAuth
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#print(df)

songs = df['Track Name'].to_string(index=False)
#print(songs)

# function to ask ChatGPT
def ask_GPT(input, key):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
    }

    data = {
        "model": "gpt-3.5-turbo",  # Change this to the desired model (e.g., "gpt-3.5-turbo")
        "messages": [{"role": "system", "content": "You are a DJ for an event. You will read the songs that are sent as the input and then create a playlist that is 10 songs long and that will be in similar style and taste to the songs submitted. None of the songs you give will be the same as the ones I feed to you. Your only output will be the names of the songs. Nothing else. You will not number the songs."},
                     {"role": "user", "content": input}]
    }

    response = requests.post(api_url, headers=headers, json=data)


    response_data = response.json()
    return response_data

key = "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"

response = ask_GPT(songs, key)
#print(response)

print('\n\ncreating AI playlist...\n')
songs_string = response['choices'][0]['message']['content']

songs_list = songs_string.strip().split('\n')[:10]
ai_df = pd.DataFrame(songs_list, columns=['Track Name']).reset_index(drop=True)

print(ai_df)



# Set up credentials for google API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\chase\Downloads\sixth-hawk-393504-f8baa14e8c72.json', scope)
client = gspread.authorize(creds)

# Open spreadsheet
spreadsheet = client.open('playlist')

# figure out where to start working -- index of where to start working in the spreadsheet -- add somethign later to start after other stuff


# add stuff to make it just append to spreadsheet instead of replacing -- online help
worksheet = spreadsheet.get_worksheet(0)

existing_data = worksheet.get_all_values()
start_row = len(existing_data) + 1
worksheet.append_rows(ai_df.values.tolist(), value_input_option='RAW', insert_data_option='OVERWRITE', table_range=f'A{start_row}')
worksheet.append_rows(df.values.tolist(), value_input_option='RAW', insert_data_option='OVERWRITE', table_range=f'A{start_row}')



