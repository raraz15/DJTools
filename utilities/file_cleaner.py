import os
from shutil import move

source_dir="/Users/recep_oguz_araz/Music/Clean_Downloads"
dest_dir="/Users/recep_oguz_araz/Music/byte_problems"

if __name__=="__main__":
    jpeg_dir="/Users/recep_oguz_araz/Projects/DJTools/Full_Pass1/not_loaded"
    file_names=os.listdir(jpeg_dir)

    for file_name in file_names:
        name,_=os.path.splitext(file_name)
        with open("out.txt","a") as outfile:
            outfile.write(name+"\n")
        move(os.path.join(source_dir,name+".mp3"),os.path.join(dest_dir,name+".mp3"))
        print(name)