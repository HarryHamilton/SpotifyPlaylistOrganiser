import time
from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint

import secrets

app = Flask(__name__)
app.secret_key = "segerghergerg"  # Random string used to sign the session
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
    current_user = sp.current_user()
    current_user_uri = current_user["uri"]

    # Gets users saved/owned playlists and stores them
    all_playlists = sp.current_user_playlists(limit=50)
    uris_of_saved_followed_playlists = []  # Array of playlist URI's that the user follows/owns
    while all_playlists:
        for i, playlist in enumerate(all_playlists['items']):
            #print("%4d %s %s" % (i + 1 + all_playlists['offset'], playlist['uri'], playlist['name']))
            uris_of_saved_followed_playlists.append(playlist['uri'])
        if all_playlists['next']:
            all_playlists = sp.next(all_playlists)
        else:
            break

    for current_playlist_uri in uris_of_saved_followed_playlists:
        current_playlist_owner = (sp.playlist(playlist_id=current_playlist_uri, fields="owner.uri"))  # Retrieves URI of owner of playlist
        print("hi")
        if str(current_playlist_owner) != ("{'owner': {'uri': '%s'}" % current_user_uri + "}"):
            #print("Len before: ")
            #print(len(uris_of_saved_followed_playlists))
            uris_of_saved_followed_playlists.remove(str(current_playlist_uri))
            #print("Len after: ")
            #print(len(uris_of_saved_followed_playlists))

    # Prints the names of the owners of the final playlists, for testing purposes to check if the code block
    # above is working correctly
    #for x in uris_of_saved_followed_playlists:
        #print("Len final: ")
        #print(len(uris_of_saved_followed_playlists))
        #print(sp.playlist(playlist_id=x, fields="owner.uri"))

    return "results in console"

    # To work on:
    # Struggling to get the program to delete the playlists that the user doesn't own from the master array.
    # I think the problem is with the .remove line, as the code DOES seem to be entering the if statement block
    # When looking at the length of the array that stores ALL playlists (followed/created), it has 132 elements,
    # which is the correct number of playlists that i do follow/own.
    # However, after the code has ran, the list that is supposed to store just the playlists I OWN has 99 elements,
    # when is should be 79. This tells me that not ALL playlists are being removed. The code must not be
    # Looping through the master list enough. Testing shows it is looping through the list 99 times, when in fact
    # it should be 130 something times.
    # I dont think it is anything to do with the spotify API, as I am getting a '200' response, which indicates
    # that the request was carried out successfully.


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
        client_id="a98aa14f0ffc4cff901798ddc9014476",
        client_secret="d99e0b64d1fe43e1926ceb97d6a0ccf8",
        redirect_uri=url_for("redirectPage", _external=True),
        scope="ugc-image-upload, user-library-read, playlist-modify-private, playlist-read-private, "
              "playlist-modify-public, "
              "playlist-read-collaborative, user-library-modify, user-read-playback-position, "
              "user-read-recently-played, user-read-private, user-read-email, user-read-playback-state, "
              "user-modify-playback-state, user-read-currently-playing, user-top-read, app-remote-control, streaming, "
              "user-follow-modify, user-follow-read "
    )
