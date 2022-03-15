#!/usr/bin/env python3
import os
import argparse

target2line = dict()
deque2BB = dict()

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-b', '--bbSequence', type=str, required=True)
    args = parser.parse_args ()

    path = args.bbSequence
    pathtemp = path + "/Lollytemp"
    files = os.listdir(pathtemp)
    for filen in files:
        if filen.startswith("sequence"):
            target = list() 
            with open(pathtemp + "/" + filen, "r") as f:
                for l in f.readlines():
                    target.append(l)

            lines = list()
            try:
                with open(pathtemp + "/B" + filen, "r") as fb:
                    for l in fb.readlines():
                       lines.append(l)
            except:
                pass

            for i in range(len(target)):
                try:
                    target2line[target[i]] = lines[i]
                except:
                    pass
    
    for filen in files:
        if filen.startswith("dequence"):
            key = "BB" + filen
            temp = list()
            try:
                with open(pathtemp + "/" + filen, "r") as f:
                    for l in f.readlines():
                       # l = l.replace("\n", "")
                       # print(l)
                        temp.append(target2line[l])
                deque2BB[key] = temp
            except Exception as e:
                print(str(e) + "-------")
    
    for key, value in deque2BB.items():
        with open(path + "/" + key, "w") as f:
            for v in value:
                f.write(v)

