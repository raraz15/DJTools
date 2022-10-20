import os
import json
import sys
import requests
import argparse

sys.path.append("/Users/recep_oguz_araz/Projects/electronic_music_downloader")

from emd.beatport.searcher import make_beatport_query
from emd.beatport.track_scraper import scrape_track

DOWNLOAD_DIR="/Users/recep_oguz_araz/Downloads"

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-n","--name",type=str,default="",help="Track Name.")
    parser.add_argument("-u","--url",type=str,default="",help="Track Name.")
    parser.add_argument("-o","--output",type=str,default=DOWNLOAD_DIR,help="Download Directory.")
    args=parser.parse_args()

    if args.url:
        beatport_url=args.url
    elif args.name:
        print("Searching Beatport...")
        beatport_url=make_beatport_query(args.name)
        print(f"Beatport URL: {beatport_url}")
    else:
        print("Must provide a track title or beatport url.")

    if not beatport_url:
        print("Beatport search failed.\nExiting")
    else:
        track_dict=scrape_track(beatport_url)
        print(json.dumps(track_dict,indent=4))
        title=f"{track_dict['Artist(s)']} - {track_dict['Title']}"
        response=requests.get(track_dict["Image URL"])
        if response.status_code==200:
            output_path=os.path.join(args.output,f"{title}.jpg")
            with open(output_path,"wb") as outfile:
                outfile.write(response.content)
            print(f"Downloaded to: {output_path}")
        else:
            print("Couldn't download the image...")
    print("Done!")