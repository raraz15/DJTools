import os
from glob import glob
import time
import scipy
import numpy as np

import matplotlib.pyplot as plt

import librosa
import librosa.display

def check_bandwidth(y,nfft,L,sr,qt,thresh=-80):
    # Calculate the spectrogram
    S=np.abs(librosa.stft(y,n_fft=nfft,hop_length=L))
    S_db=librosa.amplitude_to_db(S,ref=np.max,top_db=-thresh)
    F,T=S_db.shape
    # Find the maximum frequency bin with energy
    indices=[]
    for t in range(T):
        spectrum=S_db[(3*F//4):,t] # Look at the top part
        energy_indices=np.where(spectrum>thresh)[0]
        if energy_indices.any():
            energy_indices=(energy_indices//qt)*qt # quantize the energy bins
            max_idx=np.max(energy_indices)
            if max_idx>0: # The middle of the spectrum is not important
                indices.append((3*F//4)+max_idx)
    # The mode of this sequence indicates the bandwidth
    mode=scipy.stats.mode(indices)
    if len(mode.mode)>0:
        mode_freq=(mode.mode/F)*(sr/2)
        return S_db,int(mode_freq)
    else:
        return S_db,0

def plot_spectrogram(spec,nfft,L,sr,title,save_dir=""):
    fig,ax=plt.subplots(figsize=(12,8))
    ax.set_title(title,fontsize=20)
    img=librosa.display.specshow(spec,
                                sr=sr,
                                n_fft=nfft,
                                #win_length=W,
                                hop_length=L,
                                ax=ax,
                                #x_coords=6+np.arange(0,54,6),
                                y_axis="hz",
                                x_axis="s")
    fig.colorbar(img,ax=ax)
    if save_dir:
        os.makedirs(save_dir,exist_ok=True)
        save_path=os.path.join(save_dir,os.path.splitext(title)[0]+".jpeg")
        fig.savefig(save_path)
    plt.close()


if __name__=="__main__":

    music_dir="/Users/recep_oguz_araz/Soulseek Downloads"
    nfft=4096
    L=nfft//2
    qt=5
    T=180 # seconds

    file_paths=sorted([path for path in glob(f"{music_dir}/*.mp3")])
    total_time=0
    for file_path in file_paths:
        start_time=time.time()
        print(f"Analyzing: {os.path.basename(file_path)}")
        sr=librosa.get_samplerate(file_path)
        y,_=librosa.load(file_path,sr=sr)
        if T<len(y)/sr:
            n=np.random.randint(0,len(y)-T*sr)
            y=y[n:n+T*sr] # Shorten the audio signal
        spec,bandwidth=check_bandwidth(y,nfft,L,sr,qt)
        if bandwidth<19000:
            title=os.path.basename(file_path)
            plot_spectrogram(spec,nfft,L,sr,title,"Figures")
        end_time=time.time()
        total_time+=end_time-start_time
print(f"{total_time:.2f} seconds total processing")
