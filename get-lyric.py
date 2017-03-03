import dbus
from lxml import html
import requests
import pdb

TOKEN = 'Kz0wSeMnCT7kgo6jGPltZ9CrsSl2OjRbF8GR4HLX6GayoE07G1GQiciXasFpImGt'

def get_current_song_info():
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                         "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus,
                                        "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    return {'artist': metadata['xesam:artist'][0], 'title': metadata['xesam:title']}

def request_song_info(song_title, artist_name):
    base_url = "https://api.genius.com"
    headers = {'Authorization': 'Bearer ' + TOKEN}
    search_url = base_url + "/search"
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)

    return response

def scrap_song_url(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)

    lyrics = tree.xpath('.//lyrics//text()')

    return lyrics

def main():
    # Get info about song currently playing on Spotify
    current_song_info = get_current_song_info()
    song_title = current_song_info["title"]
    artist_name = current_song_info["artist"]

    print('{} by {}'.format(song_title, artist_name))

    # Search for matches in request response
    response = request_song_info(song_title, artist_name)
    json = response.json()
    remote_song_info = None

    for hit in json["response"]["hits"]:
        if artist_name.lower() in hit["result"]["primary_artist"]["name"].lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if song was found
    if remote_song_info:
        song_url = remote_song_info["result"]["url"]
        lyrics = scrap_song_url(song_url)
        print("\n".join(lyrics))
    else:
        print("The lyrics for this song were not found!")

if __name__ == '__main__':
    main()
