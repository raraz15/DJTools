import os
import sys
import re
import requests
from glob import glob
import argparse
from shutil import move

from mutagen import File
from mutagen.id3 import ID3,APIC,TDRL,TPE1,TIT2,TCON,TPUB

from file_name_organizer import clean_file_name

sys.path.append("/Users/recep_oguz_araz/Projects/electronic_music_downloader")

from emd.beatport.searcher import make_beatport_query
from emd.beatport.track_scraper import scrape_track

KEYS=["APIC", # Image
    "TDRL",   # ReleaseTime
    "TPE1",   # Artist
    "TIT2",   # Title
    "TCON",   # Genre
    "TPUB"]   # Publisher
EXT=[".mp3",".flac",".wav"]

# TODO: during beatport search if track has tags, use them
def main(file_path,clean):
    file_name=os.path.basename(file_path)
    file_name,ext=os.path.splitext(file_name)
    # File name cleaning
    clean_name=clean_file_name(file_name) # Required for beatport search
    if clean:
        dir_path=os.path.dirname(file_path)
        clean_file_path=os.path.join(dir_path,clean_name+ext)
        if file_name!=clean_name: # Change file name if cleaning changes it
            print(f"Changing the name to:\n{clean_name}")
            move(file_path,clean_file_path)
            file_path=clean_file_path
    # Load the ID3
    print(f"Cleaning the tags...")
    try:
        audio=ID3(file_path)
    except:
        # Create a simple tag if it did not exist
        audio=File(file_path,easy=True)
        audio.add_tags()
        audio.save()
        audio=ID3(file_path)
    # Remove unnecessary keys directly
    for key in list(audio.keys()):
        if key not in KEYS:
            audio.setall(key,[])
    # Clean and format the tags
    for key in list(audio.keys()):
        # Only check non-image and non-time-stamp keys
        if  key not in["APIC","TDRL"]:
            # Strip the url
            txt=audio[key].text[0]
            txt=re.sub(r"\s*www\..*\.com","",txt)
            txt=re.sub(r"\s*.*\.com","",txt)
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

    # Search if any of the tags don't exist
    failed=False
    for key in KEYS:
        failed+=key not in list(audio.keys())
    # If a tag is missing search for it in Beatport
    try:
        # Fill the missing information
        if failed:
            print("Some of the tags are missing. Making a Beatport query....")
            # Scrape Information from beatport
            beatport_url=make_beatport_query(clean_name)
            track_dict=scrape_track(beatport_url)
            # Fill each tag if necessary
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
    except Exception:
        print("Beatport search or filling failed!")
        pass
    audio.save(v2_version=3)

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    parser.add_argument("-c","--clean",action="store_true",help="Clean the name of the audio files.")
    args=parser.parse_args()

    # Find the audio file paths
    file_paths=[]
    for ext in EXT:
        file_paths+=[path for path in glob(f"{args.path}/*{ext}")]
    file_paths=sorted(file_paths)
    print(f"{len(file_paths)} tracks found in:\n{args.path}")

    print("Starting the formatting...")
    for i,file_path in enumerate(file_paths):
        print(f"{i+1}/{len(file_paths)}")
        print(f"Input name:\n{os.path.basename(file_path)}")
        try:
            main(file_path,args.clean)
        except KeyboardInterrupt:
            sys.exit()
        except:
            pass
        print()
    print("Done!")