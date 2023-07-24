"""
Chase Leibowitz
M&TSI 2023
7/21/23
Get the user's top tracks from the Spotify API and save it as a dataframe
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
YOUR_MACHINE_IP = "10.102.194.37"  # e.g., "192.168.x.x"
REDIRECT_URI = f"http://{YOUR_MACHINE_IP}:8000/callback"

# Set scope for API -- scope is to get top songs
scope = 'user-top-read'

# Create a spotipy client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, scope=scope))


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
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
            super().do_GET()


# Start the HTTP server
with socketserver.TCPServer(("", 8000), MyHTTPRequestHandler) as httpd:
    print(f"Server started at http://{YOUR_MACHINE_IP}:8000")
    httpd.serve_forever()
