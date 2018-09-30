import requests
from urllib.parse import urlparse
import json
import os
import time
from constants import *


def authorize(auth_code=None):

    payload = {'redirect_uri':'http://localhost', 'client_id': SPOTIFY_CLIENT_ID, 'client_secret': SPOTIFY_CLIENT_SECRET}

    if auth_code is None:
        #CHANGE SCOPES HERE
        scopes = ["user-modify-playback-state", "user-read-playback-state", "playlist-read-private", "playlist-read-collaborative", "streaming"]

        print("\n\nGo to the following url, and after clicking ok, copy and paste the link you are redirected to from your browser starting with 'localhost'\n")
        print("https://accounts.spotify.com/authorize/?client_id=" + SPOTIFY_CLIENT_ID + "&response_type=code&redirect_uri=http://localhost&scope=" + "%20".join(scopes))

        url = input("\nPaste localhost url: ")
        parsed_url = urlparse(url)
        payload['grant_type'] = 'authorization_code'
        payload['code'] = parsed_url.query.split('=')[1]
        auth_code = {}

    else:
        payload['grant_type'] = 'refresh_token'
        payload['refresh_token'] = auth_code["refresh_token"]


    result = requests.post("https://accounts.spotify.com/api/token", data=payload)

    response_json = result.json()
    cur_seconds = time.time()
    auth_code['expires_at'] = cur_seconds + response_json["expires_in"] - 60
    auth_code['access_token'] = response_json["access_token"]

    if "refresh_token" in response_json:
        auth_code['refresh_token'] = response_json["refresh_token"]

    with open('auth.json', 'w') as outfile:
        json.dump(auth_code, outfile)
    return auth_code


def get_valid_auth_header():
    with open('auth.json', 'r') as infile:
        auth = json.load(infile)
    if time.time() > auth["expires_at"]:
        auth = authorize(auth)
    return {"Authorization": "Bearer " + auth["access_token"]}


#returns a list of devices that have spotify connect linked to this device that can be controlled
def get_devices():
    headers = get_valid_auth_header()
    devices = requests.get("https://api.spotify.com/v1/me/player/devices", headers=headers).json()
    return devices


#Plays a spotify context on the currently active device.
#if a device_id is passed it will be played on a certain device
#context uri can be a playlist album or artist
#this can be changed to be a 'uris' array which can contain an array of songs to play
def play_on_device(context_uri, device_id=None):
    headers = get_valid_auth_header()
    params = {}
    if device_id is not None:
        params['device_id'] = device_id

    payload = {'context_uri': context_uri}
    response = requests.put("https://api.spotify.com/v1/me/player/play", params=params, headers=headers, json=payload)
    print(response)


#Pauses music on what ever device is activley listening.
#A device_id can be specified to only pause if its playing on a certain device
def pause_active_music(device_id=None):
    headers = get_valid_auth_header()
    params = {}
    if device_id is not None:
        params['device_id'] = device_id

    response = requests.put("https://api.spotify.com/v1/me/player/pause", headers=headers, params=params)
    print(response)


#Sets the volume from 0-100 of the currently active device
#A device_id can be specified to set the volume of a specific device
def set_device_volume(volume, device_id=None):
    headers = get_valid_auth_header()
    params = {'volume_percent': volume}
    if device_id is not None:
        params['device_id'] = device_id

    response = requests.put("https://api.spotify.com/v1/me/player/volume", headers=headers, params=params)
    print(response)



def get_playlists(limit=None, offset=None):
    headers = get_valid_auth_header()
    params = {}
    if limit is not None:
        params['limit'] = limit

    if offset is not None:
        params['offset'] = offset
    return requests.get("https://api.spotify.com/v1/me/playlists", headers=headers).json()


if not os.path.isfile('auth.json'):
    auth = authorize()



### The following code will take the first playlist on the account and start playing it on the first available connected device
# devices = get_devices()
# playlists = get_playlists()
#
# first_playlist_uri = playlists['items'][0]['uri']
# first_device_id = devices['devices'][0]['id']
# play_on_device(device_id=first_device_id, context_uri=first_playlist_uri)

### how to pause music or set the volume of an active device
# set_device_volume(30)
# pause_active_music()

#print('')