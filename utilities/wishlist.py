import os
from glob import glob
import argparse

from duplicate_finder import parse_track_title

EXT=[".mp3",".flac",".wav"]

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    parser.add_argument("-w","--wish",type=str,required=True,help="Path to wishes.txt file.")
    args=parser.parse_args()

    file_names=[]
    for ext in EXT:
        file_names+=[os.path.basename(path) for path in glob(f"{args.path}/*{ext}")]
    file_names=sorted(file_names)

    with open(args.wish,"r") as infile:
        wish_names=infile.read().split("\n")

    wishes={}
    for wish_name in wish_names:
        artist,name,version,label=parse_track_title(wish_name)
        wishes[wish_name]={"artist":artist,
                            "name":name,
                            "version":version,
                            "label":label
                            }

    existings={}
    for file_name in file_names:
        title,ext=os.path.splitext(file_name)
        artist,name,version,label=parse_track_title(title)
        existings[title]={"artist":artist,
                            "name":name,
                            "version":version,
                            "label":label
                            }

    for wish_name,dct in wishes.items():
        for exist_name,e_dct in existings.items():
            if f"{dct['artist']} - {dct['name']}" == f"{e_dct['artist']} - {e_dct['name']}":
                print("A wish is found on the collection.")
                print(wish_name)
                print(exist_name)
                print("="*60)
                break