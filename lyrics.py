import sys
from bs4 import BeautifulSoup
import requests
import argparse
import numpy as np
import re


def get_content_soup_from_url(url):
    result = requests.get(url)
    content = result.text
    return BeautifulSoup(content, "lxml")


def clean_text(text):
    """Given a string of text return clean text
    Clean issues with text
    "1. Hola" --> "Hola" 
    "Hola." --> "Hola" 
    "Hola (L)" --> "Hola"
    "Hola (1790)"  --> "Hola"
    "Hola 1790"  --> "Hola"
    """
    if type(text) == 'list':
        clean_text = []
        for t in text:
            t = re.sub(r"\(.*?\)", "", t)
            t = re.sub(r"[0-9]", "", t)
            t = t.replace(".", "")
            clean_text.append(t.strip())
        return clean_text

    else:
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"[0-9]", "", text)
        text = text.replace(".", "")
        return text.strip()



def process_row(row):
    """ Inputs a row of a table and returns the song, album and url

    The input should follow this format:
        <tr valign="bottom">
        <td align="left">
        Ain't No Cure For Love </td>
        <td align="left">
        <a href="album9.html" style="text-decoration:none">I'm Your Man (L)</a> </td>
        </tr>
    Ouputs: three strings, as shown in the example
        "Ain't No Cure For Love", "I'm Your Man", "album9.html"

    To ensure cleanliness and avoid duplicates, the following actions are performed:
      -- remove "(L)"
      -- remove years
    from album names and song names
    """
    pair = row.find_all('td')
    song = clean_text(str(pair[0].text))
    album = clean_text(pair[1].text)
    html =  row.find('a',href=True)
    return song, album, html['href']


def get_albums():
    """ Scrape album names from 
    "https://www.leonardcohenfiles.com/songind.html"

    Return a list of unique names in alfabetical order
    To ensure cleanliness and avoid duplicates, the following actions are performed:
      -- remove "(L)"
      -- remove years
    """
    url = "https://www.leonardcohenfiles.com/songind.html"
    soup = get_content_soup_from_url(url)

    tables = soup.find_all('table')
    album_table = tables[1]
    rows = album_table.find_all('tr')

    albums = set()
    for s in rows:
        pair = s.find_all('td')
        album = clean_text(pair[1].text)
        albums.add(album)
    return sorted(list(albums))


def get_songs():
    """ Scrape song urls from
    "https://www.leonardcohenfiles.com/songind.html"

    Return a list of unique names in alfabetical order
    Some cleaning to avoid duplicates:
      -- remove "(L)"
    """
    url = "https://www.leonardcohenfiles.com/songind.html"
    soup = get_content_soup_from_url(url)

    tables = soup.find_all('table')
    album_table = tables[1]
    rows = album_table.find_all('tr')

    songs = set()
    for s in rows:
        pair = s.find_all('td')
        song = clean_text(pair[0].text)
        songs.add(song)
    return sorted(list(songs))


def scrape_lyrics_from_url(song, url):
    """ Given a song and a url return the lyric of the song
    
    Inputs:
       song: string example: "Bird on the Wire"
       url: 'https://www.leonardcohenfiles.com/album2.html'
    
    Return the text of the lyrics:
    
    Like a bird on the wire,
    like a drunk in a midnight choir
    I have tried in my way to be free.
    Like a worm on a hook, 
    ...
    
    """
    soup = get_content_soup_from_url(url)
    songs = soup.find_all('h2')

    flag = 'True'
    for i in range(len(songs)):
        if clean_text(songs[i].text).lower() == song.lower():
            lyrics = soup.find_all('blockquote')[i-1]
            new_lyrics = ''
            for line in lyrics:
                new_line = re.sub(r'\<(.*?)\>', '', str(line))
                new_lyrics += new_line
            return new_lyrics.strip()
        else:
            flag = 'False'
            continue

        if flag == 'False':
            return "This song is not in the album."


def get_lyrics(s):
    """ Given an input song scrape and return the lyric
    """
    url = "https://www.leonardcohenfiles.com/songind.html"
    soup = get_content_soup_from_url(url)

    tables = soup.find_all('table')
    album_table = tables[1]
    rows = album_table.find_all('tr')

    flag = 'True'
    for r in rows:
        if s.lower() == clean_text(r.find('td').text).lower():
            # print(type(r.find_all('td')[1].text))
            if (r.find_all('td')[1].text.strip()).endswith('(L)'):
                # print(r.find_all('td')[1].text)
                link = r.find('a', href=True)
                url = "https://www.leonardcohenfiles.com/" + link['href']
                # print(url)
                return scrape_lyrics_from_url(s, url)
            else:
                flag = 'False'
                continue

        if flag == 'False':
            return "This song has no lyrics available."



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", help="Generates a list of songs", action='store_true')
    parser.add_argument("-a", help="Generates a list of albums", action='store_true')
    parser.add_argument("-l", help="Print lyrics for a given song", type=str)
    args = parser.parse_args()
    if args.s:
        songs = get_songs()
        for song in songs:
            print(song)
    if args.a:
        albums = get_albums()
        for a in albums:
            print(a)
    if args.l:
        lyric = get_lyrics(args.l)
        if lyric is None:
            print("No lyric was found")
        else:
            print(lyric)
