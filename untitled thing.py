"""
Chase Leibowitz and Adie Guo
M&TSI 2023
7/21/23
Get the user's top tracks from the Spotify API and save it as a dataframe
"""
"""
                    ,
                    "id": [track["id"] for track in top_tracks['items']], #unique song id, just in case we need it
                    "album_cover": [track["album"]["images"][0]["url"] for track in top_tracks["items"]], #for the GUI
                    "duration_ms": sp.audio_features([track["id"] for track in top_tracks['items']])[21], #duration in ms. when time runs up, next song plays
                    "popularity": [track["popularity"] for track in top_tracks['items']], #range from 0-100. for ordering songs
                    "danceability": sp.audio_features([track["id"] for track in top_tracks['items']])[10],#range from 0-1. for ordering songs
                    "energy": sp.audio_features([track["id"] for track in top_tracks['items']])[11], #0 to 1. for ordering songs
                    "valence": sp.audio_features([track["id"] for track in top_tracks['items']])[19], #0 to 1. higher happier. lower sadder. for ordering songs.
                    "key": sp.audio_features([track["id"] for track in top_tracks['items']])[12], # 0 = C, 1 = C♯/D♭, 2 = D, and so on, -1 is NA. for mixing
                    "tempo": sp.audio_features([track["id"] for track in top_tracks['items']])[20], #avg bpm. for mixing
                    "time_signature": sp.audio_features([track["id"] for track in top_tracks['items']])[22], #time signature. for mixing
"""

import os
import pandas as pd
import webbrowser
import spotipy
from spotipy import SpotifyOAuth
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Get ID and secret from environment
client_id = "0eac05c214004561ab6bd69a504e2594"
client_secret = "008c275d524146d68a9ec0cd04540dfc"

# Replace with your machine's IP
YOUR_MACHINE_IP = "10.251.158.107"  # e.g., "192.168.x.x"
REDIRECT_URI = f"http://{YOUR_MACHINE_IP}:8888/callback"

# Set scope for API -- scope is to get top songs
scope = 'user-top-read'

# Create a spotipy client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, scope=scope))
df = pd.DataFrame()
playlist_name = "Verse Playlist"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self, df):
        # If the path is the root, redirect to Spotify authentication
        if self.path == "/" or self.path == "":
            auth_url = sp.auth_manager.get_authorize_url()
            self.send_response(302)  # 302 is a redirect status code
            self.send_header('Location', auth_url)
            self.end_headers()
            return

        # Check if the path is /callback
        elif self.path.startswith("/callback"):
            # Extract the code from the callback URL
            query_components = parse_qs(urlparse(self.path).query)
            code = query_components.get("code", [None])[0]

            if code:
                # Get the access token using the code
                token_info = sp.auth_manager.get_access_token(code)
                sp.token = token_info["access_token"]

                # Get the current authenticated user's username
                current_user_info = sp.me()
                username = current_user_info["id"]

                # Fetch the user's top tracks
                top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')

                data = {
                    "Track Name": [track["name"] for track in top_tracks["items"]],
                    "Artist": [", ".join([artist["name"] for artist in track["artists"]]) for track in
                               top_tracks["items"]],
                    "Album": [track["album"]["name"] for track in top_tracks["items"]],
                    "Release Date": [track["album"]["release_date"] for track in top_tracks["items"]]
                }

                # Convert to DataFrame
                df = pd.DataFrame(data)
                print(df)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authentication successful! You can close this window.")
                return

            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Failed to authenticate!")
                return

        # If it's neither root nor callback, serve files as usual
        else:
            super().do_GET(df)
            super().createPlaylist(df)


    def search_track(track_name, artist_name):
        # Search for the track on Spotify
        query = f"track:{track_name} artist:{artist_name}"
        search_result = sp.search(query, limit=1, type='track')

        if search_result['tracks']['items']:
            return search_result['tracks']['items'][0]['uri']
        else:
            return None

    def create_playlist(playlist_name):
        # Create a new playlist
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
        return playlist['id']

    def add_tracks_to_playlist(playlist_id, track_uris):
        # Add tracks to the playlist
        sp.playlist_add_items(playlist_id, track_uris)

    def createPlaylist(df):
        df.sort_values(["energy","valence"], ascending=[True, True], na_position="last")
        playlist_id = sp.create_playlist(playlist_name)
        track_uris = []
        for _, row in df.iterrows():
            track_name = row['Track Name']
            artist_name = row['Artist Name']
            track_uri = sp.search_track(track_name, artist_name)
            if track_uri:
                track_uris.append(track_uri)

        if track_uris:
            sp.add_tracks_to_playlist(playlist_id, track_uris)
            print(f"Playlist '{playlist_name}' with {len(track_uris)} tracks created successfully!")
        else:
            print("No tracks found on Spotify. Playlist creation failed.")


# Start the HTTP server
with socketserver.TCPServer(("", 8888), MyHTTPRequestHandler) as httpd:
    print(f"Server started at http://{YOUR_MACHINE_IP}:8888")
    httpd.serve_forever()