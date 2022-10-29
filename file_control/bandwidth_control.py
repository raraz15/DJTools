import os
import time
import argparse
from glob import glob
import datetime as dt
import scipy
import numpy as np

import matplotlib.pyplot as plt

import librosa
import librosa.display

DATE=dt.datetime.strftime(dt.datetime.now(),"%d_%m_%Y")

def check_bandwidth(y,nfft,L,sr,qt,thresh=-110):
    # Calculate the spectrogram
    S=np.abs(librosa.stft(y,n_fft=nfft,hop_length=L))
    S_db=librosa.amplitude_to_db(S,ref=np.max,top_db=-thresh)
    F,T=S_db.shape
    F_start=4*F//5
    # Find the maximum frequency bin with energy
    indices=[]
    for t in range(T):
        spectrum=S_db[F_start:,t] # Look at the top part
        energy_indices=np.where(spectrum>thresh)[0]
        if energy_indices.any():
            energy_indices=(energy_indices//qt)*qt # quantize the energy bins
            max_idx=np.max(energy_indices)
            if max_idx>0: # The middle of the spectrum is not important
                indices.append(F_start+max_idx)
    # The mode of this sequence indicates the bandwidth
    mode=scipy.stats.mode(indices)
    if len(mode.mode)>0:
        mode_freq=(mode.mode/F)*(sr/2)
        return S_db,int(mode_freq)
    else:
        return S_db,0

def algo2(y,nfft,L,sr,qt,thresh=-110):
    # Calculate the spectrogram
    S=np.abs(librosa.stft(y,n_fft=nfft,hop_length=L))
    S_db=librosa.amplitude_to_db(S,ref=np.max,top_db=-thresh)
    F,T=S_db.shape
    F_start=4*F//5
    F_start=3*F//4
    found=False
    for f in range(F_start,F)[::-1]:
        p=100*len(np.where(S_db[f,:]>thresh)[0])/len(S_db[f,:])
        if p>=55:
            found=True
            break
    if found:
        return S_db, int((f/F)*(sr/2))
    else:
        return S_db, 0

# TODO: plot the actual time
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
        plt.clf()
        plt.close(fig)

nfft=4096
L=nfft//2
qt=5
thresh=-110
T=240 # seconds

# TODO: Check clipping
if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    parser.add_argument("-o","--output",type=str,default=DATE,help="Directory for saving the sptectrograms.")
    args=parser.parse_args()

    success_dir=os.path.join(args.output,"success")
    fail_dir=os.path.join(args.output,"fail")
    os.makedirs(success_dir,exist_ok=True)
    os.makedirs(fail_dir,exist_ok=True)

    file_paths=sorted([path for path in glob(f"{args.path}/*.mp3")])
    total_time=0
    for file_path in file_paths:
        start_time=time.time()
        print(f"Analyzing: {os.path.basename(file_path)}")
        sr=librosa.get_samplerate(file_path)
        y,_=librosa.load(file_path,sr=sr)
        if T<len(y)/sr:
            n=np.random.randint(0,len(y)-T*sr)
            y=y[n:n+T*sr] # Shorten the audio signal
        spec,bandwidth=check_bandwidth(y,nfft,L,sr,qt,thresh=thresh)
        print(f"Detected bandwidth: {bandwidth:.1f}Hz")
        if bandwidth<19500:
            title=os.path.basename(file_path)
            plot_spectrogram(spec,nfft,L,sr,title,fail_dir)
        else:
            title=os.path.basename(file_path)
            plot_spectrogram(spec,nfft,L,sr,title,success_dir)
        end_time=time.time()
        total_time+=end_time-start_time
        print(f"{end_time-start_time:.4f} seconds file")
        print("="*60)
    print(f"{total_time:.2f} seconds total processing")
