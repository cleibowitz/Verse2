import os
import pandas as pd
import spotipy
from spotipy import SpotifyOAuth
from urllib.parse import urlparse, parse_qs
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import requests
from flask import Flask, render_template, redirect, request

# Constants
CLIENT_ID = "0eac05c214004561ab6bd69a504e2594"
CLIENT_SECRET = "008c275d524146d68a9ec0cd04540dfc"
YOUR_MACHINE_IP = "10.102.194.37"
REDIRECT_URI = f"http://{YOUR_MACHINE_IP}:8000/callback"
SCOPE = 'user-top-read'
GOOGLE_CREDENTIALS_PATH = 'PATH_TO_YOUR_GOOGLE_CREDENTIALS_JSON'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'


# Spotify Authentication
def authenticate_user():
    sp_temp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, cache_path=None))
    auth_url = sp_temp.auth_manager.get_authorize_url()
    return auth_url


def save_top_tracks_to_google_sheets(sp):
    # Retrieve top tracks
    results = sp.current_user_top_tracks(limit=50)
    track_list = []
    for idx, item in enumerate(results['items']):
        track = item['name']
        track_list.append([idx + 1, track, item['artists'][0]['name']])
    df = pd.DataFrame(track_list, columns=["Rank", "Track Name", "Artist"])

    # Authenticate Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Google Sheet Name").sheet1

    # Save to Google Sheets
    set_with_dataframe(sheet, df)


def download_songs_from_google():
    # Authenticate Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Google Sheet Name").sheet1

    # Get data from Google Sheets
    df = get_as_dataframe(sheet, usecols=[1, 2], skiprows=1)
    df = df.dropna()

    return df


def ask_GPT_and_save(input):
    key = "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"

    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
    }

    data = {
        "model": "gpt-3.5-turbo",  # Change this to the desired model (e.g., "gpt-3.5-turbo")
        "messages": [{"role": "system",
                      "content": "You are a DJ for an event. You will read the songs that are sent as the input and then create a playlist that is 10 songs long and that will be in similar style and taste to the songs submitted. None of the songs you give will be the same as the ones I feed to you. Your only output will be the names of the songs. Nothing else. You will not number the songs."},
                     {"role": "user", "content": input}]
    }

    songs_string = response['choices'][0]['message']['content']

    songs_list = songs_string.strip().split('\n')[:10]
    ai_df = pd.DataFrame(songs_list, columns=['Track Name']).reset_index(drop=True)


    # Authenticate Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Google Sheet Name for AI Recommendations").sheet1

    # Save AI recommendations to Google Sheets
    set_with_dataframe(sheet, ai_df)

    return ai_df


def make_spotify_playlist(df):


# ... [This function will need more information about the structure of your df and how you intend to create the playlist.]

# Flask Routes
app = Flask(__name__)


@app.route('/')
def index():
    return authenticate_user()


@app.route('/callback')
def callback():
    # Get access token
    code = request.args['code']
    sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, cache_path=None)
    token_info = sp_oauth.get_access_token(code)
    token = token_info['access_token']

    # Create Spotify object with permissions
    sp = spotipy.Spotify(auth=token)

    # Call function to save top tracks to Google Sheets
    save_top_tracks_to_google_sheets(sp)

    return redirect('http://localhost:8080/next_process')  # Replace with wherever you want to redirect after success.


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

    # Step 2: Download songs from Google
    df = download_songs_from_google()

    # Step 3: Use GPT-3 to recommend songs and save results to Google Sheets
    songs = df['Track Name'].to_string(index=False)
    ai_df = ask_GPT_and_save(songs)

    # Step 4: Make Spotify playlist
    final_df = pd.concat([df, ai_df], ignore_index=True)
    make_spotify_playlist(final_df)
