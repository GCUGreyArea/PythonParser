#!/usr/bin/env python3

import sys

def read_series(filename):
    with open(filename, mode='rt',encoding='utf-8') as f:
        return [int(line.strip()) for line in f]
    
def main(filename):
    S = read_series(filename)
    print(S)

if __name__ == '__main__':
    main(sys.argv[1])
