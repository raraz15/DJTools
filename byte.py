import os
import sys
from glob import glob
import time
import argparse

import warnings
#warnings.filterwarnings("error")

import librosa

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    file_paths=sorted([path for path in glob(f"{args.path}/*.mp3")])
    total_time=0
    for file_path in file_paths:
        print("="*100)
        print(f"Analyzing: {os.path.basename(file_path)}")
        start_time=time.time()
        try:
            sr=librosa.get_samplerate(file_path)
            y,_=librosa.load(file_path,sr=sr)
            if len(y)==0:
                print("0 samples returned.")
        except KeyboardInterrupt:
            sys.exit()
        except:
            print("Unexpected Error!")
        end_time=time.time()
        total_time+=end_time-start_time
    print(f"{total_time:.2f} seconds total processing")