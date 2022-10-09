import os
from glob import glob
import argparse
import re

from mutagen import File
from mutagen.id3 import ID3,TPE1,TPE2,TIT2,TALB,TCON,TPUB

KEYS=["APIC","TDRC","TDRL","TDOR","TPE1","TIT2","TALB","TCON","TPUB","TDRL"]

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    file_paths=sorted([path for path in glob(f"{args.path}/*.mp3")])

    for file_path in file_paths:
        _,ext=os.path.splitext(file_path)
        if ext!=".mp3":
            continue
        try:
            audio=ID3(file_path)
        except: # Create the simple tag
            audio=File(file_path,easy=True)
            audio.add_tags()
            audio.save()
            audio=ID3(file_path)
        # Remove unnecessary keys directly
        for key in list(audio.keys()):
            if key not in KEYS:
                audio.setall(key,[])
        # Clean the tags from URLs
        for key in list(audio.keys()):
            if "APIC" not in key and key!="TDRC" and key!="TDRL" and key!="TDOR": # Check each key except the image
                txt=audio[key].text[0]
                txt=re.sub(r"\s*www\..*\.com","",txt)
                txt=re.sub(r"\s*.*\.com","",txt)
                if txt:
                    if key=="TPE1":
                        audio['TPE1']=TPE1(encoding=3,text=txt)
                    elif key=="TPE2":
                        audio['TPE2']=TPE2(encoding=3,text=txt)
                    elif key=="TIT2":
                        audio['TIT2']=TIT2(encoding=3,text=txt)
                    elif key=="TALB":
                        audio['TALB']=TALB(encoding=3,text=txt)
                    elif key=="TCON":
                        audio['TCON']=TCON(encoding=3,text=txt)
                    elif key=="TPUB":
                        audio['TPUB']=TPUB(encoding=3,text=txt)
                else:
                    audio.setall(key,[]) # Remove key if no string remains