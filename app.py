from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import secrets

app = Flask(__name__)
app.secret_key = ""  # Random string used to sign the session
app.config["SESSION_COOKIE_NAME"] = "Spotify Playlist Organiser"


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

    return "redirect"


@app.route("/getTracks")
def getTracks():
    return "Get tracks page"


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="",
        client_secret="",
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-library-read"
    )
