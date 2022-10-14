import os
import argparse
from glob import glob
import re
from shutil import move

EXT=[".mp3",".flac",".wav"]

# TODO: , with ,\s
def clean_file_name(file_name):
    """Expects the file name without the extension."""

    if " " not in file_name:
        # if_the_file-name_is_like_this
        file_name=re.sub("_"," ",file_name)
        file_name=re.sub("-"," - ",file_name)
        file_name=file_name.title()
    file_name=re.sub(r"\A[^a-zA-Z]+","",file_name) # Track number, or leading whitespaces
    file_name=re.sub(r"\s+\Z","",file_name) # Trailing whitespaces
    file_name=re.sub(r"\s\s+"," ",file_name) # Multiple whitespaces
    m=re.search(r"\[.*[M|m]ix\]",file_name) # Replace [] with () around the Mix
    if m:
        file_name=file_name[:m.start()]+f"({m[0][1:-1]})"+file_name[m.end():]
    m=re.search(r"\([^\)]*[M|m]ix\)",file_name)
    if m: # Capitalize Mix type
        file_name=file_name[:m.start()]+f"{m[0]}".title()+file_name[m.end():]
    file_name=re.sub(r"www\..*\.[com|net]","",file_name)
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
    if "(feat. " in file_name: # - remains in the end
        idx=file_name.find(" - ")
        m=re.search(r"\s\(feat\.[^\()]+\)",file_name)
        if m.start()>idx:
            feat_str=m.group()
            file_name=re.sub(r"\s\(feat\.[^\()]+\)","",file_name)
            file_name=file_name[:idx]+feat_str+file_name[idx:]
    file_name=re.sub(";",",",file_name)
    file_name=re.sub("Dj","DJ",file_name)
    file_name=re.sub(r"[0-9][A-Z]\s-\s[0-9]*\s-\s","",file_name) # Key,BPM
    file_name=re.sub(r"\s-\s[0-9][A-Z]\s-\s[0-9]*","",file_name) # Key,BPM
    file_name=re.sub(r"\s\-\s+\Z","",file_name) # - remains in the end
    return file_name

# TODO: look at version, audio length...
def find_duplicates(file_names):
    for i in range(len(file_names)-1):
        file_name0=file_names[i]
        file_name1=file_names[i+1]
        title0,ext0=os.path.splitext(file_name0)
        title1,ext1=os.path.splitext(file_name1)
        if ext0!=ext1:
            continue
        else: # TODO: What if there is no - in the name?
            title_chunks0=title0.split(" - ")
            title_chunks1=title1.split(" - ")
            artist0=title_chunks0[0]
            rest0=title_chunks0[1]
            artist1=title_chunks1[0]
            rest1=title_chunks0[1]
            # Compare artists
            if artist0!=artist1:
                continue
            else:
                # Compare the first words of the rest
                word0=rest0.split(" ")[0]
                word1=rest1.split(" ")[0]
                if word0!=word1:
                    continue
                else:

                    print("Same files found:")
                    print(title0+ext0)
                    print(title1+ext1)
                    print()
                    ## This is where it gets dangerous, some titles dont have version info
                    ## Compare the titles except the version
                    #title_mix_chunk0=title_chunks0[1].split(" (")
                    #title_mix_chunk1=title_chunks1[1].split(" (")
                    #if title_mix_chunk0[0]!=title_mix_chunk1[0]:
                    #    continue
                    #else:
                    #    # Compare the mix types
                    #    if len(title_mix_chunk0)>1 and len(title_mix_chunk1) >1:
                    #        if ")" in title_mix_chunk0[1] and ")" in title_mix_chunk1[1]:
                    #            mix0=title_mix_chunk0[1].split(")")[0]
                    #            mix1=title_mix_chunk1[1].split(")")[0]
                    #            #print(mix0,mix1)
                    #            if mix0!=mix1:
                    #                continue
                    #            else:
                    #                print("Same files!")
                    #                print(title0+ext0)
                    #                print(title1+ext1)
                    #                print()
                    #    else:
                    #        continue

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to directory containing audio files.")
    args=parser.parse_args()

    # Find the names of audio files
    file_names=[]
    for ext in EXT:
        file_names+=[os.path.basename(path) for path in glob(f"{args.path}/*{ext}")]
    file_names=sorted(file_names)
    # Clean the names
    clean_file_names=[]
    for i,file_name in enumerate(file_names):
        file_name,ext=os.path.splitext(file_name)
        print(f"\n{i+1}/{len(file_names)}")
        print(f"Input name:\n{file_name}")
        try:
            clean_name=clean_file_name(file_name)
            print(f"Cleaned name:\n{clean_name}")
            clean_file_names.append((file_name+ext,clean_name+ext))
        except:
            print("="*40)
            print("File name couldn't be cleaned!")
            print("="*40)
    # Change the names
    for file_name,clean_name in clean_file_names:
        if file_name!=clean_name:
            move(os.path.join(args.path,file_name),os.path.join(args.path,clean_name))
    print("Done!")
