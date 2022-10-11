import os
import unicodedata
import json
import xml.etree.ElementTree as ET
import argparse

def replace_non_ascii(str):
    str=unicodedata.normalize('NFKD', str).encode('ascii', 'ignore')
    str=str.decode("utf-8") # For json dump
    return str

if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--path",type=str,required=True,help="Path to .xml file")
    args=parser.parse_args()

    tree=ET.parse(args.path)
    root=tree.getroot()
    #for child in root:
    #    print(child.tag)
    collection=root[1]
    track_dicts={idx:track.attrib for idx,track in enumerate(collection)}

    for idx,track_dict in enumerate(track_dicts):
        track_dicts[idx]["Genre"]=replace_non_ascii(track_dicts[idx]["Genre"])
        track_dicts[idx]["Name"]=replace_non_ascii(track_dicts[idx]["Name"])

    file_name=os.path.splitext(os.path.basename(args.path))[0]
    with open(f"{file_name}.json","w") as outfile:
        json.dump(track_dicts,outfile,indent=4)
