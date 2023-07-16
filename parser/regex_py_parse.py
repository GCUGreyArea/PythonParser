# Simple python test for regex

import re
import json 

def match_aws_regex(St):
    Re = '^aws: (?P<json>{.*})'
    Match = re.search(Re, St)
    return Match.group('json') 


def main():
    St = 'aws: {"name":"Barry Robinson","position":"Lead cyber engineer"}'
    Json = match_aws_regex(St)    
    Dict = json.loads(Json)
    print( Dict )

if __name__ == '__main__':
    main()