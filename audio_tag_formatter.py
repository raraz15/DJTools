import os
import sys
from glob import glob
import argparse
from shutil import move

from utils.file_name_organizer import clean_file_name
from tag_formating import mp3_tag_formatter,flac_tag_formatter,wav_tag_formatter

EXT=[".mp3",".flac",".wav"]

# TODO: cleaning, moving function
if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    parser.add_argument("-c","--clean",action="store_true",help="Clean the name of the audio files.")
    args=parser.parse_args()

    # Find the audio file paths
    file_paths=[]
    for ext in EXT:
        file_paths+=glob(f"{args.path}/*{ext}")
    file_paths=sorted(file_paths)
    print(f"{len(file_paths)} tracks found in:\n{args.path}")

    print("Starting the tag formatting...")
    try:
        for i,file_path in enumerate(file_paths):
            print("="*80)
            print(f"{i+1}/{len(file_paths)}")
            file_name=os.path.basename(file_path)
            print(f"Input:\n{file_name}")
            file_name,ext=os.path.splitext(file_name)
            # File name cleaning
            clean_name=clean_file_name(file_name) # Required for beatport search
            if args.clean:
                dir_path=os.path.dirname(file_path)
                clean_file_path=os.path.join(dir_path,clean_name+ext)
                if file_name!=clean_name: # Change file name if cleaning changes it
                    print(f"Changing the name to:\n{clean_name+ext}")
                    move(file_path,clean_file_path)
                    file_path=clean_file_path
            if ext==".mp3":
                mp3_tag_formatter(file_path)
            if ext==".wav":
                wav_tag_formatter(file_path)
            elif ext==".flac":
                flac_tag_formatter(file_path)
            else:
                print("Unsupported file type!")
    except KeyboardInterrupt:
        sys.exit()
    print("="*80)
    print("Done!")