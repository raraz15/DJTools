import os
import argparse
from glob import glob
import re
from shutil import move

EXT=[".mp3",".flac",".wav"]

def clean_file_name(file_name):
    file_name=re.sub(r"\A[^a-zA-Z]+","",file_name) # Track number, or leading whitespaces
    file_name=re.sub(r"\s+\Z","",file_name) # Trailing whitespaces
    file_name=re.sub(r"\s\s+"," ",file_name) # Multiple whitespaces
    m=re.search(r"\[.*[M|m]ix\]",file_name) # Replace [] with () around the Mix
    if m:
        file_name=file_name[:m.start()]+f"({m[0][1:-1]})"+file_name[m.end():]
    m=re.search(r"\([^\)]*[M|m]ix\)",file_name)
    if m: # Capitalize Mix type
        file_name=file_name[:m.start()]+f"{m[0]}".title()+file_name[m.end():]
    file_name=re.sub(r"www\..*\.com","",file_name)
    # Deal with feat
    file_name=re.sub(r"Feat|Ft|ft",r"feat",file_name)
    m=re.search(r"feat",file_name)
    if m and file_name[m.end():m.end()+2]!=". ":
        file_name=file_name[:m.start()]+"feat. "+file_name[m.end():]
    m=re.search(r"feat\. ",file_name) # Enclose remixer name in parantheses
    if m and file_name[m.start()-1]!="(":
        feat_remixer="feat. "+" ".join(file_name[m.end():].split(" ")[:2])
        file_name=re.sub(feat_remixer,f"({feat_remixer})",file_name)
    if "feat. " in file_name:
        # Remove the feat artist from the Producers part
        m=re.search(r"\(feat\.[^\()]+\)",file_name)
        remixer=file_name[m.start()+7:m.end()-1]
        idx=file_name.find(remixer)
        if m.start()+7!=idx:
            file_name=file_name[:idx-2]+file_name[idx+len(remixer):]
    # Change the (feat. ) position
    if "(feat. " in file_name:
        idx=file_name.find(" - ")
        m=re.search(r"\s\(feat\.[^\()]+\)",file_name)
        if m.start()>idx:
            feat_str=m.group()
            file_name=re.sub(r"\s\(feat\.[^\()]+\)","",file_name)
            file_name=file_name[:idx]+feat_str+file_name[idx:]
    file_name=re.sub(";",",",file_name)
    # - remains in the end
    file_name=re.sub(r"\s\-\s+\Z","",file_name)
    return file_name

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    # Find the names of audio files
    file_names=[]
    for ext in EXT:
        file_names+=[os.path.basename(path) for path in glob(f"{args.path}/*{ext}")]
    # Clean the names
    clean_file_names=[]
    for file_name in file_names:
        file_name,ext=os.path.splitext(file_name)
        clean_name=clean_file_name(file_name)
        clean_file_names.append((file_name+ext,clean_name+ext))
    # Change the names
    for file_name,clean_name in clean_file_names:
        if file_name!=clean_name:
            move(os.path.join(args.path,file_name),os.path.join(args.path,clean_name))
    print("Done!")
