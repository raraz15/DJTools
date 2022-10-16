import os
import re
import requests
from glob import glob
import argparse

EXT=[".mp3",".flac",".wav"]

def parse_track_title(title):
    """Provide without file extension"""

    if " - " in title:
        m=re.search(r"\(.*-.*\)",title) # When the version has a - in it
        if m:
            idx=title.index(" - ")
            artist=title[:idx]
            rest=title[idx:]
        else:
            artist,rest=title.split(" - ")
    else:
        artist=""
        rest=title

    m=re.search(r"\([^\)]*[M|m]ix\)",rest)
    if m:
        version=m.group()
        name=rest[:m.start()-1]
    else: # It should be the "feat" or "with"
        version=""
        name=rest

    m=re.search(r"\[.*\]",title)
    if m:
        label=m.group()
    else:
        label=""
    return artist,name,version,label

# TODO: look at version, audio length...
def find_duplicates(file_names):
    for i in range(len(file_names)-1):
        file_name0=file_names[i]
        file_name1=file_names[i+1]
        title0,ext0=os.path.splitext(file_name0)
        title1,ext1=os.path.splitext(file_name1)
        artist0,name0,version0,label0=parse_track_title(title0)
        artist1,name1,version1,label1=parse_track_title(title1)
        if name0!=name1:
            continue
        else:
            if artist0!=artist1:
                continue
            else:
                if version0==version1:
                    if ext0==ext1:
                        print("Same files found:")
                        print(file_name0)
                        print(file_name1)
                        print()
                    else:
                        print("Same files with different extension found:")
                        print(file_name0)
                        print(file_name1)
                        print()
                else:
                    print("Same track with different versions found.")
                    print(file_name0)
                    print(file_name1)
                    print()

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    # Search for duplicates
    file_names=[]
    for ext in EXT:
        file_names+=[os.path.basename(path) for path in glob(f"{args.path}/*{ext}")]
    file_names=sorted(file_names)
    
    find_duplicates(file_names)