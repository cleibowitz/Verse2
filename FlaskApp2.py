from flask import Flask, redirect, url_for, session
import pandas as pd
import spotipy
from spotipy import SpotifyOAuth
from flask import request

app = Flask(__name__)
app.secret_key = "some_random_string"  # Replace this with your own secret key

# Your Spotify credentials
client_id = "0eac05c214004561ab6bd69a504e2594"
client_secret = "008c275d524146d68a9ec0cd04540dfc"
redirect_uri = 'http://10.102.194.37:5000/callback'

received_token = None  # Global variable to store the received token


@app.route('/')
def index():
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                            scope='user-top-read')
    auth_url = sp_oauth.get_authorize_url()
    return f'<h1>Authenticate with <a href="{auth_url}">Spotify</a></h1>'


@app.route('/callback')
def callback():
    print("Callback route accessed!")
    code = request.args.get('code')
    print(f"Received code: {code}")

    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-top-read')
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        return "Error getting the access token."

    print(f"Access Token: {token_info['access_token']}")

    return redirect(url_for('receive_token', token=token_info['access_token']))




@app.route('/receive_token/<token>')
def receive_token(token):
    global received_token
    received_token = token
    print("token recieved")

    # Now you can create a Spotify client with the token and fetch data
    sp = spotipy.Spotify(received_token)

    # Get the authenticated user's profile information
    user_info = sp.current_user()
    session['username'] = user_info['id']  # Save the username in the session

    # Fetch the top tracks and display them
    top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
    data = {
        "Track Name": [track["name"] for track in top_tracks["items"]],
        "Artist": [", ".join([artist["name"] for artist in track["artists"]]) for track in top_tracks["items"]],
        "Album": [track["album"]["name"] for track in top_tracks["items"]],
        "Release Date": [track["album"]["release_date"] for track in top_tracks["items"]]
    }

    df = pd.DataFrame(data)
    return df.to_html()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
