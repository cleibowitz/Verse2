import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import os

# Assuming your dataframe is df and the column with song names is named "song_names"
# df = pd.read_csv('your_file.csv')  # Uncomment this if you're reading from a CSV

# Set up credentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\chase\Downloads\sixth-hawk-393504-f8baa14e8c72.json', scope)
client = gspread.authorize(creds)

# open spreadsheet
spreadsheet = client.open('playlist')

# figure out where to start working -- index of where to start working in the spreadsheet -- add somethign later to start after other stuff
worksheet = spreadsheet.get_worksheet(0)

existing_data = worksheet.get_all_values()
len_data = len(existing_data)

# download data from spreadsheet and save as df
df = get_as_dataframe(worksheet, evaluate_formulas=True, skiprows=0)


# delete all of the empty rows and columns that get imported
df = df.dropna(how='all')
df = df.dropna(axis=1, how='all')

print(df)

# Spotify credentials
SPOTIPY_CLIENT_ID = '0eac05c214004561ab6bd69a504e2594'
SPOTIPY_CLIENT_SECRET = '008c275d524146d68a9ec0cd04540dfc'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="playlist-modify-private,playlist-modify-public"))

# Get user id
user_id = sp.current_user()['id']

# overwrite existing playlists with same name
playlists = sp.user_playlists(user_id)
for playlist in playlists['items']:
    if playlist['name'] == "Verse":
        sp.user_playlist_unfollow(user_id, playlist['id'])

# Create a new playlist
playlist = sp.user_playlist_create(user_id, "Verse", public=True)
playlist_id = playlist['id']

# Add songs to the playlist
added_track_ids = []

# Initialize empty dataframe to store track details
track_data = {
    'ID': [],
    'Album Cover': [],
    'Duration (ms)': [],
    'Popularity': [],
    'Danceability': [],
    'Energy': [],
    'Valence': [],
    'Key': [],
    'Tempo': [],
    'Time Signature': []
}
track_df = pd.DataFrame(track_data)

for song in df['Track Name']:
    if not song or pd.isna(song):  # Check for empty or NaN values
        continue

    try:
        search_result = sp.search(song, limit=1, type='track')
        track = search_result['tracks']['items'][0]
        track_id = track['id']

        # Check for duplicates before adding
        if track_id not in added_track_ids:
            # Get audio features for the track
            audio_features = sp.audio_features(track_id)[0]

            # Append data to the dataframe
            track_df.loc[track_id] = {
                'ID': track_id,
                'Album Cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'Duration (ms)': track['duration_ms'],
                'Popularity': track['popularity'],
                'Danceability': audio_features['danceability'],
                'Energy': audio_features['energy'],
                'Valence': audio_features['valence'],
                'Key': audio_features['key'],
                'Tempo': audio_features['tempo'],
                'Time Signature': audio_features['time_signature']
            }

            sp.playlist_add_items(playlist_id, [track_id])
            added_track_ids.append(track_id)
            print("added: " + str(song))

        else:
            print(f"Duplicate song {song} skipped.")

    except IndexError:
        print(f"Couldn't find {song} on Spotify.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error searching for {song}. Error: {e}")

print(track_df)  # This will print your dataframe with the required details

print(f"Playlist created: {playlist['external_urls']['spotify']}")

print(f"Playlist created: {playlist['external_urls']['spotify']}")


# Assuming your dataframe is named 'df'
file_name = "output.xlsx"
with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
    track_df.to_excel(writer, sheet_name='Sheet1', index=False)

# Open the file
os.system(f'start excel "{file_name}"')  # for Windows


