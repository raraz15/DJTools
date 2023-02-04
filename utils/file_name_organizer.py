import os
import argparse
from glob import glob
import re
from shutil import move

EXT=[".mp3",".flac",".wav"]


# TODO: Better Version Capitalize
def file_name_cleaner(file_name):
    """Expects the file name without the extension."""

    # Delete the BPM and Key information from Leading and Trailing
    file_name=re.sub(r"\A[0-9]{1,2}[A-B]\s-\s[0-9]{0,3}\s-\s","",file_name)
    file_name=re.sub(r"\A[0-9]{0,3}\s-\s[0-9]{1,2}[A-B]\s-\s","",file_name)
    file_name=re.sub(r"\s-\s[0-9]{1,2}[A-B]\s-\s[0-9]{0,3}\Z","",file_name)
    file_name=re.sub(r"\s-\s[0-9]{0,3}\s-\s[0-9]{1,2}[A-B]\Z","",file_name)
    # if_the_file-name_is_like_this
    if " " not in file_name:
        file_name=re.sub("_"," ",file_name)
        file_name=re.sub("-"," - ",file_name)
        file_name=file_name.title()
    # Leading and Trailing whitespaces
    file_name=re.sub(r"\A\s+","",file_name)
    file_name=re.sub(r"\s+\Z","",file_name)
    # Remove track number
    file_name=re.sub(r"\A[0-9]{1,}\s{0,1}(\.|-){0,1}\s{0,1}","",file_name)
    # Multiple whitespaces
    file_name=re.sub(r"\s\s+"," ",file_name)
    # Replace [] with () around the Mix
    m=re.search(r"\[.*(M|m)ix\]",file_name)
    if m:
        file_name=file_name[:m.start()]+f"({m[0][1:-1]})"+file_name[m.end():]
    # Capitalize Mix type
    m=re.search(r"\([^\)]*(M|m)ix\)",file_name)
    if m:
        file_name=file_name[:m.start()]+f"{m[0]}".title()+file_name[m.end():]
    # Remove urls
    file_name=re.sub(r"\s*-*\s*www\..*\.(com|net|org)\s*","",file_name)
    # main
    file_name=re.sub(r"\s-\s*main\s[0-9]{3}","",file_name)
    # Deal with feat
    file_name=re.sub(r"Feat",r"feat",file_name)
    file_name=re.sub(r"\sFt\s*"," feat",file_name)
    file_name=re.sub(r"\sft\s*"," feat",file_name)
    m=re.search(r"feat",file_name)
    if m and file_name[m.end():m.end()+2]!=". ":
        file_name=file_name[:m.start()]+"feat. "+file_name[m.end():]
    m=re.search(r"feat\. ",file_name) # Enclose feat name in parantheses
    if m and file_name[m.start()-1]!="(":
        feat_remixer=file_name[m.end():].split(" ")[:2] # Take the next 2 words
        if "(" in feat_remixer[-1]: # If the artist has a single word name
            feat_remixer.pop(-1)
        feat_remixer="feat. "+" ".join(feat_remixer)
        file_name=re.sub(feat_remixer,f"({feat_remixer})",file_name)
    if "feat. " in file_name:
        # Remove the feat artist from the Producers part
        m=re.search(r"\(feat\.[^\()]+\)",file_name)
        remixer=file_name[m.start()+7:m.end()-1]
        idx=file_name.find(remixer)
        if m.start()+7!=idx:
            file_name=file_name[:idx-2]+file_name[idx+len(remixer):]
    if "(feat. " in file_name: # - remains in the end
        idx=file_name.find(" - ")
        m=re.search(r"\s\(feat\.[^\()]+\)",file_name)
        if m and m.start()>idx:
            feat_str=m.group()
            file_name=re.sub(r"\s\(feat\.[^\()]+\)","",file_name) # Is this a bug?
            file_name=file_name[:idx]+feat_str+file_name[idx:]
    # Further Cleaning
    file_name=re.sub(";",",",file_name)
    file_name=re.sub("Dj","DJ",file_name)
    #file_name=re.sub(r"\s\-\s+\Z","",file_name) # - 
    return file_name

def clean_file_path(file_path):
    file_name=os.path.basename(file_path)
    dir_path=os.path.dirname(file_path)
    file_name,ext=os.path.splitext(file_name)
    print(f"File name: {file_name}{ext}")
    clean_file_name=file_name_cleaner(file_name)
    if file_name!=clean_file_name:
        print(f"Cleaned file name: {clean_file_name}{ext}")
        dest_path=os.path.join(dir_path,clean_file_name+ext)
        move(file_path,dest_path)
        return dest_path
    else:
        return file_path

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    # Get the paths of audio files
    file_paths=sorted([path for ext in EXT for path in glob(f"{args.path}/*{ext}")])
    print(f"{len(file_paths)} tracks found in:\n{args.path}")
    # Clean the names of the files
    for i,file_path in enumerate(file_paths):
        print("="*80)
        print(f"[{i+1}/{len(file_paths)}]")
        clean_file_path(file_path)
    print("="*40)
    print("Done!")
