#!/usr/bin/env python3

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--line', type=str, required=True, help="need to merge.")
    args = parser.parse_args()
    map = {}
    tmp = ""
    with open(args.line, 'r') as f:
        for l in f.readlines():
            fun = l.strip().split("\t")[0]
            li = l.strip().split("\t")[1]
            if  fun != tmp :
                tmp = fun
                map[fun] = li
    with open(args.line, 'w') as f:
        for key, value in map.items():
            f.write(key + '\t' + value + '\n')

# Main function
if __name__ == '__main__':
    main()
            
