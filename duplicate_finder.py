import os
import re
import requests
from glob import glob
import argparse

EXT=[".mp3",".flac",".wav"]

# TODO: look at version, audio length...
def find_duplicates(file_names):
    for i in range(len(file_names)-1):
        file_name0=file_names[i]
        file_name1=file_names[i+1]
        title0,ext0=os.path.splitext(file_name0)
        title1,ext1=os.path.splitext(file_name1)

        if " - " in title0:
            title_chunks0=title0.split(" - ")
            artist0=title_chunks0[0]
            if len(title_chunks0)==2:
                rest0=title_chunks0[1]
            else:
                rest0=""
        else:
            artist0=""
            rest0=title_chunks0
        if " - " in title1:
            title_chunks1=title1.split(" - ")
            artist1=title_chunks1[0]
            if len(title_chunks1)==2:
                rest1=title_chunks1[1]
            else:
                rest1=""
        else:
            artist1=""
            rest1=title_chunks1

        if "(" in rest0:
            m=re.search(r"\([^\)]*[M|m]ix\)",rest0)
            if m:
                version0=m.group()
                name0=rest0[:m.start()-1]
            else:
                version0=""
                name0=rest0
        else:
            name0=rest0
            version0=""
        if "(" in rest1:
            m=re.search(r"\([^\)]*[M|m]ix\)",rest1)
            if m:
                version1=m.group()
                name1=rest1[:m.start()-1]
            else:
                version1=""
                name1=rest1
        else:
            name1=rest1
            version1=""

        if name1!=name0:
            continue
        else:
            if artist0!=artist1:
                continue
            else:
                print("Same files found:")
                print(file_name0)
                print(file_name1)
                print()

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    # Search for duplicates
    file_paths=[]
    for ext in EXT:
        file_paths+=[os.path.basename(path) for path in glob(f"{args.path}/*{ext}")]
    file_paths=sorted(file_paths)
    find_duplicates(file_paths)