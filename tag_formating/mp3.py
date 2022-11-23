import os,sys
import re
import requests

from mutagen import File
from mutagen.id3 import ID3,APIC,TDRL,TPE1,TIT2,TCON,TPUB

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

def first_load(file_path):
    try:
        audio=ID3(file_path)
    except:
        # Create a simple tag if it did not exist
        audio=File(file_path,easy=True)
        audio.add_tags()
        audio.save(v2_version=3)

def clean_tags(file_path):
    audio=ID3(file_path)
    # Remove unnecessary keys directly
    print("Removing unnecessary tags...")
    for key in list(audio.keys()):
        if (key not in KEYS) and (KEYS[0] not in key): # Keep APIC
            audio.setall(key,[])
    # Clean and format the tags
    print(f"Formating remaining tags...")
    for key in list(audio.keys()):
        # Only check non-time-stamp keys and non-image
        if (key!="TDRL") and (KEYS[0] not in key):
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
                audio.setall(key,[]) # Remove key if no string remains
    # Save the tags
    audio.save(v2_version=3)

# TODO: get track name from tags or title? do not use clean_file_name
def find_missing_tags(file_path):
    audio=ID3(file_path)
    # Check the existence of each key
    check={}
    for key in KEYS:
        if key=="APIC": # APIC has many forms all including the keyword APIC
            cover_exists=False
            for k in list(audio.keys()):
                cover_exists=cover_exists or (KEYS[0] in k)
            check[key]=cover_exists
        else:
            if key in list(audio.keys()):
                check[key]=True
            else:
                check[key]=False
    all_exist=True
    for key,val in check.items():
        all_exist=all_exist and val
    # If any tag is missing search for it in Beatport
    if not all_exist:
        print("Some necessary tags are missing. Making a Beatport query....")
        file_name=os.path.splitext(os.path.basename(file_path))[0]
        clean_name=file_name_cleaner(file_name)
        # Scrape Information from beatport
        beatport_url=make_beatport_query(clean_name)
        print(f"Beatport URL: {beatport_url}")
        if not beatport_url:
            print("Beatport search failed.")
        else:
            track_dict=scrape_track(beatport_url)
            # Fill tags if missing
            for key,val in check.items():
                if not val and key=="TPE1":
                    txt=track_dict["Artist(s)"]
                    audio['TPE1']=TPE1(encoding=3,text=txt)
                    print(f"Artist tag saved: {txt}")
                elif not val and key=="TIT2":
                    txt=track_dict["Title"]
                    if track_dict["Mix"]:
                        txt+=f" ({track_dict['Mix']})"
                    audio['TIT2']=TIT2(encoding=3,text=txt)
                    print(f"Title tag saved: {txt}")
                elif not val and key=="TCON":
                    txt=track_dict["Genre"]
                    audio['TCON']=TCON(encoding=3,text=txt)
                    print(f"Genre tag saved: {txt}")
                elif not val and key=="TPUB":
                    txt=track_dict["Label"]
                    audio['TPUB']=TPUB(encoding=3,text=txt)
                    print(f"Label tag saved: {txt}")
                elif not val and key=="TDRL":
                    txt=track_dict["Released"]
                    audio['TDRL']=TDRL(encoding=3,text=txt)
                    print(f"Released tag saved: {txt}")
                elif not val and KEYS[0] in key:
                    req=requests.get(track_dict["Image URL"])
                    audio["APIC"]=APIC(3,'image/jpg',3,'Front cover',req.content)
                    print(f"Album Cover saved")
        # Save the tags
        audio.save(v2_version=3)
        print("Saved the tags!")

def mp3_tag_formatter(file_path):
    first_load(file_path) # Load the ID3 tags
    clean_tags(file_path) # Clean the tags
    find_missing_tags(file_path) # Fill missing information