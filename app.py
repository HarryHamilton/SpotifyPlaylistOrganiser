import time
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

import secrets

app = Flask(__name__)
app.secret_key = ""  # Random string used to sign the session
app.config["SESSION_COOKIE_NAME"] = "Spotify Playlist Organiser"
TOKEN_INFO = "token_info"


# Sets up pages/endpoints for the website
@app.route("/")
def login():
    sp_oath = create_spotify_oauth()
    auth_url = sp_oath.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirect")
def redirectPage():
    """This will be where the user is redirected to after
    completing the OAuth
    """
    sp_oath = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oath.get_access_token(code)
    session[TOKEN_INFO] = token_info

    return redirect(url_for("getTracks", _external=True), )



@app.route("/getTracks")
def getTracks():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")  # Redirect user to login page if they aren't logged in

    sp = spotipy.Spotify(auth=token_info["access_token"])

    result = sp.current_user_playlists(limit=50)
    users_saved_followed_playlists = []  # Array of playlist URI's that the user follows/owns
    while result:
        for i, playlist in enumerate(result['items']):
            print("%4d %s %s" % (i + 1 + result['offset'], playlist['uri'], playlist['name']))
            users_saved_followed_playlists.append(playlist['uri'])
        if result['next']:
            result = sp.next(result)
        else:
            result = None
    print(users_saved_followed_playlists)
    return "results in console"


def get_token():
    """ Ensures valid token data exists.
    - Check that is hasn't expired. If it has, refresh it.
    - If token data never existed (e.g. user never signed in), redirect
    the user to the login page.
    """
    # Checks if token data exists (i.e. if user is logged in or not)
    token_info = session.get(TOKEN_INFO, None)  # "None" will be stored if no token data exists
    if not token_info:
        raise "exception"

    # If token data exists, check that it hasn't expired. Refresh the token if it has
    now = int(time.time())
    is_expired = token_info["expires_at"] - now < 60
    if is_expired:
        sp_oath = create_spotify_oauth()
        token_info = sp_oath.get_refresh_access_token(token_info["refresh_token"])
    return token_info



def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri=url_for("redirectPage", _external=True),
        scope="ugc-image-upload, user-library-read, playlist-modify-private, playlist-read-private, "
              "playlist-modify-public, "
              "playlist-read-collaborative, user-library-modify, user-read-playback-position, "
              "user-read-recently-played, user-read-private, user-read-email, user-read-playback-state, "
              "user-modify-playback-state, user-read-currently-playing, user-top-read, app-remote-control, streaming, "
              "user-follow-modify, user-follow-read "
    )
