import os
import argparse
from shutil import move

source_dir="/Users/recep_oguz_araz/Music/Clean_Downloads"
dest_dir="/Users/recep_oguz_araz/Music/byte_problems"

# TODO: name as DATE
if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--source",type=str,required=True,help="Path of source directory of all audio files.")
    parser.add_argument("-d","--dest",type=str,required=True,help="Path of destination directory of audio files.")
    parser.add_argument("-p","--path",type=str,required=True,help="Path of directory containing which files to move.")
    args=parser.parse_args()

    # Move each file that exists in args.path from args.source to args.dest
    for file_name in os.listdir(args.path):
        name,_=os.path.splitext(file_name)
        # Write the name of these files to a text file
        with open("out.txt","a") as outfile:
            outfile.write(name+"\n")
        move(os.path.join(args.source,name+".mp3"),os.path.join(args.dest,name+".mp3"))
        print(name)