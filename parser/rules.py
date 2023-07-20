#!/usr/bin/env python3

import sys
import yaml
import os

def load_yaml(FName):
    f = open(FName)
    return yaml.load(f, Loader=yaml.FullLoader)


def get_patterns_by_id(FName):
    Y = load_yaml(FName)

    PBI = {}
    PBN = {}
    TMap = {}
    RList = []
    JList = []
    TMap = {'json': JList, 'regex':RList}
    Ptns = Y[0]['patterns']
    for P in Ptns:
        PBI[P['id']] = P['pattern']
        PBN[P['name']] = P['pattern']
        if P['type'] == 'regex':
            RList.append(P['pattern'])
        elif P['type'] == 'json':
            JList.append(P['pattern'])
        elif P['type'] == 'kv':
            JList.append(P['pattern'])
            
    return [PBI,PBN,TMap]

def main(file):
    x = get_patterns_by_id(file)
    print( x )

if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print('please supply a file to parse')
    else: 
        main(sys.argv[1])