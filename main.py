from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Spotify Client ID and Secret
CLIENT_ID = '0eac05c214004561ab6bd69a504e2594'
CLIENT_SECRET = '008c275d524146d68a9ec0cd04540dfc'
REDIRECT_URI = 'http://10.102.194.37:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'

@app.route('/')
def index():
    auth_link = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=user-read-private"
    return f'<h1>Click <a href="{auth_link}">here</a> to authenticate with Spotify.</h1>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    post_request = requests.post('https://accounts.spotify.com/api/token', data=token_data)

    response_data = post_request.json()

    access_token = response_data.get("access_token")
    refresh_token = response_data.get("refresh_token")
    token_type = response_data.get("token_type")
    expires_in = response_data.get("expires_in")

    # For now, let's just display the access token.
    # In a real app, you'd likely store it for future use.
    return jsonify(access_token=access_token)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
