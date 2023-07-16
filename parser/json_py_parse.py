# Simple python test for json

import json
import sys
import copy



def make_key(current,key):
    c = ''
    if current == '.':
        return "".join(['.',key])
    else:
        return "".join([current,'.',key])


# Render the json map into a searchable jq structure
# this can be indexed simply using jq paths such as 
# .name.some_name[idx].value 
def interate_through_dict(Dict, current):
    print(Dict)
    HashDict = {}
    for key,value in Dict.items():
        if type(value) is str:
            k = make_key(current,key)
            HashDict[k] = value
        elif type(value) is dict:
            k = make_key(current,key)
            Nh = interate_through_dict(value,k)
            HashDict.update(Nh)
        elif type(value) is list:
            k = make_key(current,key)
            idx = "".join([k,'[]'])
            HashDict[idx] = value
            count = 0
            for item in value:
                if type(item) is dict:
                    idx = "".join([k,'[',str(count),']'])
                    Nh = interate_through_dict(item,idx)
                    HashDict.update(Nh)
                else: 
                    idx = "".join([k,'[',str(count),']'])
                    HashDict[idx] = item
                count += 1

    return HashDict


def parse_json(JSon):
    Dict = json.loads(JSon)
    HDict = interate_through_dict(Dict,'.')
    print(HDict)

def main(JSon):
    parse_json(JSon)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('please supply a json string to parse')
    else: 
        print(sys.argv[1])
        main(sys.argv[1])

parse_json( '{"name":"Barry Robinson","dob":"5-10-1964", "roles":{"software engineering":"team lead","skils":["java","c++","python",{"c++":"excelent","java":"avarage","python":"beginer"}]}}' )