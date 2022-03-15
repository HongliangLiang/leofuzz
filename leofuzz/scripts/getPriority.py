#!/usr/bin/env python3
import os
import argparse

def lcs_len(a, b):
    n = len(a)
    m = len(b)
    
    l = [([0] * (m + 1)) for i in range(n + 1)]
    direct = [([0] * m) for i in range(n)]#0 for top left, -1 for left, 1 for top
    
    for i in range(n + 1)[1:]:
        for j in range(m + 1)[1:]:
            if a[i - 1] == b[j - 1]:
                l[i][j] = l[i - 1][j - 1] + 1
            elif l[i][j - 1] > l[i - 1][j]: 
                l[i][j] = l[i][j - 1]
                direct[i - 1][j - 1] = -1
            else:
                l[i][j] = l[i - 1][j]
                direct[i - 1][j - 1] = 1
                
    return l
 

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-p', '--priority', type=str, required=True)
    args = parser.parse_args ()

    path = args.priority
    lists = []
    tmp = []
    with open(path + "/runtimeseq.txt", "r") as f:
        for l in f.readlines():
            if l[0] == "#":
                if len(tmp) != 0:
                   lists.append(list(tmp))
                   tmp = []
            else:
                tmp.append(l)
    res = []
    for i in range(len(lists)):
        val = 0
        for j in range(len(lists)):
            if i != j :
               t = lcs_len(lists[i], lists[j])
               if t[len(lists[i])][len(lists[j])] / max(len(lists[i]), len(lists[j])) >= 0.4:
                   val = val + 1
        res.append(val)
    
    with open(path + "/priority.txt", "w") as f:
        for i in range(len(res)):
            f.write(str(res[i]) + "\n")                  



