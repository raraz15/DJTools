# coding: utf-8
import os
from glob import glob
import argparse
from shutil import move

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to Spotify playlist JSON file.")
    args=parser.parse_args()

    for path in glob(f"{args.path}/*.webp"):
        move(path, os.path.splitext(path)[0])

