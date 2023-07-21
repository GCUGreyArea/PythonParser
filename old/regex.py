#!/usr/bin/env python3

import re
import sys

def test(reg,str):
    match = re.compile(reg)
    Sr = match.search(str)
    print(Sr)
    print(Sr.group(1))



def main(reg,str):
    test(reg,str)

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])