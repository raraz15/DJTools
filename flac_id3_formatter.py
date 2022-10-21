import os
import sys
import argparse
from glob import glob

from mutagen.flac import FLAC

KEYS=["artist","title","label","genre","release date","year"]

# TODO: put artwork
if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    file_paths=glob(f"{args.path}/*.flac")

    for i,file_path in enumerate(file_paths):
        print("="*80)
        print(f"{i+1}/{len(file_paths)}")
        file_name=os.path.basename(file_path)
        file_name,ext=os.path.splitext(file_name)
        print(f"Input name:\n{file_name}")
        audio=FLAC(file_path)
        for key in audio.keys():
            if key not in KEYS:
                audio.pop(key)
        audio.save()
    print("="*80)
    print("Done!")