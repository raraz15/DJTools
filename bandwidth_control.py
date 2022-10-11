import os
from glob import glob
import time
import scipy
import numpy as np

import librosa

def check_bandwidth(y,nfft,sr,qt,thresh=-80):
    # Calculate the spectrogram
    S=np.abs(librosa.stft(y,n_fft=nfft))
    S_db=librosa.amplitude_to_db(S,ref=np.max,top_db=-thresh)
    F,T=S_db.shape
    S_db=S_db[F//2:,:] # Look only at the top part
    indices=[]
    for t in range(T):
        spectrum=S_db[:,t] # Look at the top part
        energy_indices=np.where(spectrum>thresh)[0]
        if energy_indices.any():
            energy_indices=(energy_indices//qt)*qt # quantize the energy bins
            indices.append(F//2+np.max(energy_indices))
    mode=scipy.stats.mode(indices)
    mode_freq=(mode.mode/F)*(sr/2)
    return int(mode_freq)

if __name__=="__main__":

    music_dir="/Users/recep_oguz_araz/Soulseek Downloads"
    nfft=4096
    qt=10
    T=120 # seconds

    file_paths=sorted([path for path in glob(f"{music_dir}/*.mp3")])

    total_time=0
    for file_path in file_paths:
        start_time=time.time()
        #print(f"Analyzing: {os.path.basename(file_path)}")
        sr=librosa.get_samplerate(file_path)
        #print(sr)
        y,_=librosa.load(file_path,sr=sr)

        try:
            n=np.random.randint(0,len(y)-T*sr)
            y=y[n:n+T*sr] # Shorten the audio signal
        except:
            print("WTF!")
            print(y.shape)

        bandwidth=check_bandwidth(y,nfft,sr,qt)
        print(bandwidth)
        print()
        end_time=time.time()
        total_time+=end_time-start_time
print(f"{total_time:.2f} seconds total processing")
