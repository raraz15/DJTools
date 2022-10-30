import sys
from glob import glob
import argparse

from utils.file_name_organizer import clean_file_path
from tag_formating import mp3_tag_formatter,flac_tag_formatter,wav_tag_formatter

EXT=[".mp3",".flac",".wav"]

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
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
            # File name cleaning
            file_path=clean_file_path(file_path)
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