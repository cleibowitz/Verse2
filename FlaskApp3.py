from flask import Flask, redirect, url_for, session
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify
import pandas as pd

app = Flask(__name__)
app.secret_key = "some_random_string"  # Replace this with your own secret key

# Spotify credentials
client_id = "0eac05c214004561ab6bd69a504e2594"
client_secret = "008c275d524146d68a9ec0cd04540dfc"
redirect_uri = 'http://10.102.194.37:5000/callback'

# Create a separate Spotify OAuth blueprint
spotify_bp = make_spotify_blueprint(client_id=client_id, client_secret=client_secret, redirect_to="callback")
app.register_blueprint(spotify_bp, url_prefix="/login")

# This signal will capture the access token after successful authentication
@spotify_bp.before_app_request
def before_request():
    if 'access_token' in session:
        # Use the access token from the session for API calls
        spotify_bp.session.token = (session['access_token'], '')
    else:
        return redirect(url_for('spotify.login'))

@app.route('/')
def index():
    # Fetch the top tracks and display them
    top_tracks = spotify.get("/v1/me/top/tracks", params={"limit": 10, "time_range": "short_term"})

    # Process the response and display the tracks (you can adjust this part to your needs)
    data = {
        "Track Name": [track["name"] for track in top_tracks.json()["items"]],
        "Artist": [", ".join([artist["name"] for artist in track["artists"]]) for track in top_tracks.json()["items"]],
        "Album": [track["album"]["name"] for track in top_tracks.json()["items"]],
        "Release Date": [track["album"]["release_date"] for track in top_tracks.json()["items"]]
    }

    return pd.DataFrame(data).to_html()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
