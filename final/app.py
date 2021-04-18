import spotipy
from IPython.core.display import clear_output
from spotipy import SpotifyClientCredentials, util
import pandas as pd
import time
import numpy as np
import csv
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
from xml.dom import minidom
import xml.etree.ElementTree as ET
from datetime import date
from flask import Flask, redirect, request, render_template, url_for
import requests as req
import shutil

client_id = '46c1cfc8247e4267b8f5516f9a61affc'
client_secret = '704027695cb84a95b86351d933d63acd'
def createSp(username):
    token = util.prompt_for_user_token(
    username=username,
    scope='playlist-modify-public playlist-read-collaborative',
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://localhost:8889/callback")
    if token: return spotipy.Spotify(auth=token)

"""
Ivan's code
Gets songs from playlist chosen by user user
returns a List of string of song IDs
"""
def getPlaylistTracksIDs(usr, username, selected=None):
    playlist = getPlaylist(usr, username, selected)
    tracks = []
    playlist = usr.user_playlist(username, playlist['id'])
    for item in playlist['tracks']['items']:

        track = item['track']
        tracks.append((track['id'], track['name']))
    return tracks

def getPlaylist(usr, username, selected=None):
    playlists = usr.user_playlists(username)
    for playlist in playlists['items']:
        print(playlist['name'])
    #chosen = input("Please type the name of playlist to match: ")
    chosen=selected
    for playlist in playlists['items']:
        if playlist['name'] == chosen: return playlist


def getUser(usrID=None):
    #user = input("Enter profile link for user: ")
    user=usrID
    user = user.replace('https://open.spotify.com/user/', '')
    user = user.split('?')
    print(user[0])
    return user[0]

def compareList(track_usr1, track_usr2):
    match = []
    for track in track_usr1:
        if track in track_usr2:
            match.append(track)
    return match

def buildPlaylist(track_usr1, track_usr2, usr1, username1):
    match = compareList(track_usr1, track_usr2)
    trackIDs = []
    #Output matches
    for track in match:
        print(track[1])
        trackIDs.append(track[0])
    if(len(trackIDs)==0):
        return redirect('/none')
    New_usr1 = usr1.user_playlist_create(username1, name = "The New Shared Playlist",
                                        public = True, collaborative = False)['uri'].split(':')[2]
    usr1.user_playlist_add_tracks(username1, New_usr1, trackIDs)
    return New_usr1

def getBarCode(playlistID):
    web = "https://scannables.scdn.co/uri/plain/png/000000/white/640/spotify:playlist:"
    web += playlistID
    response = req.get(web, stream=True)
    file = open("static/sample_image.png", "wb")
    file.write(response.content)
    file.close()

def getNewPlaylistID(usr1, username1):
    id = str(usr1.user_playlists(username1)['items'][0]['uri'])
    id = id.split(':')
    id = id[2]
    return id


app = Flask(__name__)
#p1=True
@app.route('/')
def home():
    with open("templates/pg1.html") as f:
        html = f.read()
    return html

@app.route('/signup', methods = ['POST'])
def signup():

    print("called user 1")
    Userlink = request.form.get('Spotify Profile Link')
    playlistName = request.form.get('Spotify Playlist Name')
    print("User link: " + Userlink)
    print("playlist name: " + playlistName)
    print()

    username1 = getUser(Userlink)
    usr1 = createSp(username1)
    track_usr1 = getPlaylistTracksIDs(usr1, username1, playlistName)

    print("called user 2")
    Userlink2 = request.form.get('Spotify Profile Link2')
    playlistName2 = request.form.get('Spotify Playlist Name2')
    print("User link: " + Userlink2)
    print("playlist name: " + playlistName2)
    print()

    username2 = getUser(Userlink2)
    usr2 = createSp(username2)
    track_usr2 = getPlaylistTracksIDs(usr2, username2, playlistName2)
    new_playlistID = buildPlaylist(track_usr1,track_usr2, usr1, username1)
    getBarCode(new_playlistID)
    return redirect('/output')

@app.route('/none')
def noMatches():
    with open("templates/error.html") as f:
        s1 = f.read()
    return s1
@app.route('/output')
def dispCode():
    with open("templates/barcodeOut.html") as f:
        html = f.read()
    return render_template("barcodeOut.html")


if __name__ =='__main__':
    app.run(host="0.0.0.0")

