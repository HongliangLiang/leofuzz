#!/usr/bin/env python3
import os
import argparse

sequences = {}

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-s', '--sequence', type=str, required=True)
    args = parser.parse_args ()

    path = args.sequence
    files = os.listdir(path)
    for filen in files:
        if "dequence" in filen:
            with open(path + "/" + filen, "r") as f:
                for l in f.readlines():
                    filename = l.strip().split(":")[0]
                    line = l.strip().split(":")[1]
                    if filename in sequences:
                        sequences[filename].add(line)
                    else :
                        sequences[filename] = set()
                        sequences[filename].add(line)
    
    for key, value in sequences.items():
        with open(path + "/" + "sequence" + "_" + key + "++++++", "w") as f:
            for v in value:
                f.write(key + ":" + v  + "\n")


