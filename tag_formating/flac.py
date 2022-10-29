import sys
import re
import json
import requests

from mutagen.flac import FLAC,Picture

KEYS=["artist","title","label","genre","release date","year"]

sys.path.append("/Users/recep_oguz_araz/Projects/electronic_music_downloader")

from emd.beatport.searcher import make_beatport_query
from emd.beatport.track_scraper import scrape_track

def clean_tags(file_path):
    audio=FLAC(file_path)
    for key in audio.keys():
        if key not in KEYS:
            audio.pop(key)
    audio.save()

def format_title_artist(file_path):
    # Read the FLAC comments
    audio=FLAC(file_path)
    artist=" , ".join(audio['artist'])
    title=audio['title'][0]
    # Format the title and the artist
    artist=re.sub(";",",",artist)
    artist=re.sub(" ,",", ",artist)
    artist=re.sub(r"\s\s+"," ",artist) # Multiple whitespaces
    title=re.sub(r"Feat|Ft|ft",r"feat",title)
    m=re.search(r"feat.*\s\(",title) # Put the feat in parantheses
    if m:
        title=title[:m.start()]+"("+m.group()[:-2]+") "+title[m.end()-1:]
    m=re.search(r"\s\(feat.*?\)",title)
    if m:
        title=title[:m.start()]+title[m.end():] # Remove feat from title
        feat_vocal=m.group()[2:-1]
        vocal=feat_vocal[6:]
        if vocal not in artist:
            artist+=" feat. "+vocal
        else:
            if "feat" not in artist:
                artist=re.sub(vocal,"",artist)
                if artist[-2:]==", ":
                    artist=artist[:-2]
                artist+=" feat. "+vocal
        artist=re.sub(r"\s\s+"," ",artist) # Multiple whitespaces
        artist=re.sub(r"\A,\s+","",artist) # Multiple whitespaces
    # Put the new comments
    audio["title"]=title
    audio["artist"]=artist
    audio.save()

def insert_artwork(file_path):
    audio=FLAC(file_path)
    if not audio.pictures:
        track=f"{audio['artist'][0]} - {audio['title'][0]}"
        print(track)
        beatport_url=make_beatport_query(track)
        if not beatport_url:
            print("Beatport search failed.")
        else:
            print(f"Beatport URL: {beatport_url}")
            track_dict=scrape_track(beatport_url)
            print(json.dumps(track_dict,indent=4))
            response=requests.get(track_dict["Image URL"])
            if response.status_code==200:
                image=Picture()
                image.type=3
                image.mime='image/jpeg'
                image.desc='front cover'
                image.data=response.content
                audio.add_picture(image)
                audio.save()
            else:
                print("Image couldn't be downloaded.")

def comment_formatter(file_path):
    clean_tags(file_path)
    format_title_artist(file_path)
    insert_artwork(file_path)