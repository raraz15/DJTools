import os,sys
import re
import requests

from mutagen.wave import WAVE
from mutagen.id3 import APIC,TDRL,TPE1,TIT2,TCON,TPUB

from utils.file_name_organizer import file_name_cleaner

sys.path.append("/Users/recep_oguz_araz/Projects/electronic_music_downloader")

from emd.beatport.searcher import make_beatport_query
from emd.beatport.track_scraper import scrape_track

KEYS=["APIC", # Image
    "TDRL",   # ReleaseTime
    "TPE1",   # Artist
    "TIT2",   # Title
    "TCON",   # Genre
    "TPUB"]   # Publisher

# TODO: simplify?
def clean_tags(file_path):
    audio=WAVE(file_path)
    print("Removing unnecessary tags...")
    # Remove unnecessary keys directly
    for key in list(audio.keys()):
        if key not in KEYS:
            audio.pop(key)
    print(f"Cleaning the texts of the tags...")
    # Clean and format the tags
    for key in list(audio.keys()):
        # Only check non-image and non-time-stamp keys
        if key not in["APIC","TDRL"]:
            # Strip the url
            txt=audio[key].text[0]
            txt=re.sub(r"\s*www\..*\.com/*","",txt)
            txt=re.sub(r"\s*.*\.com/*","",txt)
            txt=re.sub(r"\s*.*\.net/*","",txt)
            # Clean the tag
            txt=re.sub(r"\s\s+"," ",txt) # Multiple
            txt=re.sub(r"\A\s+","",txt) # Leading
            txt=re.sub(r"\s+\Z","",txt) # Trailing
            # Put it where it belongs, if a text is remaining
            if txt:
                if key=="TPE1":
                    audio['TPE1']=TPE1(encoding=3,text=txt)
                elif key=="TIT2":
                    audio['TIT2']=TIT2(encoding=3,text=txt)
                elif key=="TCON":
                    audio['TCON']=TCON(encoding=3,text=txt)
                elif key=="TPUB":
                    audio['TPUB']=TPUB(encoding=3,text=txt)
            else:
                audio.pop(key) # Remove key if no string remains
    # Save the tags
    audio.save(v2_version=3)

def find_missing_tags(file_path):
    audio=WAVE(file_path)
    # Search if any of the tags don't exist
    failed=False
    for key in KEYS:
        failed+=key not in list(audio.keys())
    # If a tag is missing search for it in Beatport
    if failed:
        print("Some of the tags are missing. Making a Beatport query....")
        file_name=os.path.splitext(os.path.basename(file_path))[0]
        clean_name=file_name_cleaner(file_name)
        # Scrape Information from beatport
        beatport_url=make_beatport_query(clean_name)
        if not beatport_url:
            print("Beatport search failed.")
        else:
            print(f"Beatport URL: {beatport_url}")
            track_dict=scrape_track(beatport_url)
            # Fill desired tags if missing
            for key in KEYS:
                if key not in list(audio.keys()):
                    if key=="TPE1":
                        txt=track_dict["Artist(s)"]
                        audio['TPE1']=TPE1(encoding=3,text=txt)
                    elif key=="TIT2":
                        txt=track_dict["Title"]
                        if track_dict["Mix"]:
                            txt+=f" ({track_dict['Mix']})"
                        audio['TIT2']=TIT2(encoding=3,text=txt)
                    elif key=="TCON":
                        txt=track_dict["Genre"]
                        audio['TCON']=TCON(encoding=3,text=txt)
                    elif key=="TPUB":
                        txt=track_dict["Label"]
                        audio['TPUB']=TPUB(encoding=3,text=txt)
                    elif key=="TDRL":
                        txt=track_dict["Released"]
                        audio['TDRL']=TDRL(encoding=3,text=txt)
                    elif key=="APIC":
                        req=requests.get(track_dict["Image URL"])
                        audio["APIC"]=APIC(3,'image/jpg',3,'Front cover',req.content)
                    else:
                        continue
        # Save the tags
        audio.save(v2_version=3)
        print("Saved the tags!")

def wav_tag_formatter(file_path):
    clean_tags(file_path) # Clean the tags
    find_missing_tags(file_path) # Fill missing information