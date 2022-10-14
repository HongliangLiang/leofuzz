#!/usr/bin/env python3

import os
import re
import networkx as nx
import pydot
import collections
import argparse

re_cglabel = re.compile(r'[{](.*?)[}]', re.S)
re_bblabel = re.compile(r'[{](.*?)[}]', re.S)
re_dot = re.compile(r':s\d+', re.S)
prefix = ""
fun2line = {}
call2line = {}
targetsfile = {}

class memoize:
  # From https://github.com/S2E/s2e-env/blob/master/s2e_env/utils/memoize.py

  def __init__(self, func):
    self._func = func
    self._cache = {}

  def __call__(self, *args):
    if not isinstance(args, collections.Hashable):
      return self._func(args)

    if args in self._cache:
      return self._cache[args]

    value = self._func(*args)
    self._cache[args] = value
    return value

  def __repr__(self):
    # Return the function's docstring
    return self._func.__doc__

  def __get__(self, obj, objtype):
    # Support instance methods
    return functools.partial(self.__call__, obj)

@memoize
def getcallgraphnode(G, name):
    n_name =  "\"{%s}\"" % name
    try:
        return [n for n, d in G.nodes(data=True) if n_name in d.get('label', '')][0]   
    except:
        return None 

@memoize
def getnode(G, name):
    n_name =  "\"{%s:" % name
    try:
        return [n for n, d in G.nodes(data=True) if n_name in d.get('label', '')][0]   
    except:
        return None 

def getfuncname(G, node):
    try:
        label = [d.get('label', '') for n, d in G.nodes(data=True) if n == node]
        return re.findall(re_cglabel, label[0])[0]
    except:
        return ""

def gettarget(G, node):
    try:
        label = [d.get('label', '') for n, d in G.nodes(data=True) if n == node]
        print(label)
        return re.findall(re_bblabel, label[0])[0]
    except:
        return ""



def predominate1(G, name, start):
    start_with = getcallgraphnode(G, start)
    dic = nx.immediate_dominators(G, start_with)
    seq = []
    temp = getcallgraphnode(G, name)
    while temp != start_with:
        seq.insert(0, fun2line[getfuncname(G, temp)])
        temp = dic[temp]
    return seq

def getallpaths(G, source, target, path, paths, pathname, pathnames):
    if source == target:
        tname = getfuncname(G, source)
        if "main" == tname:
            tname = prefix + tname
        path.insert(0, fun2line[tname])
        pathname.insert(0, getfuncname(G, source))
        paths.append(path)
        pathnames.append(pathname)
        return
    try:
        tname = getfuncname(G, source)
        if "main" == tname:
            tname = prefix + tname
        path.insert(0, fun2line[getfuncname(G, target)])
        pathname.insert(0, getfuncname(G, target))
    except:
        pass
    i = 0
    temp = list(path)
    tempname = list(pathname)
    for predecessor in G.predecessors(target):
        try:
            prename = getfuncname(G, predecessor)
            if "main" == prename:
                prename = prefix + prename
            if fun2line[prename] in path:
                continue
        except:
            pass
        if i == 0:
            i = i + 1
            getallpaths(G, source, predecessor, path, paths, pathname, pathnames)
        else:
            p = list(temp)
            pname = list(tempname)
            getallpaths(G, source, predecessor, p, paths, pname, pathnames)
     
def getpath(G, source, target):
    source = getcallgraphnode(G, source)
    if "main" in target:
        target = "main"
    target = getcallgraphnode(G, target)
    paths = list()
    pathnames = list()
    if not nx.algorithms.shortest_paths.generic.has_path(G, source, target):
        temp = []
        temp.append(fun2line[getfuncname(G, target)])
        tempname = []
        tempname.append(getfuncname(G, target))

        paths.append(temp)
        pathnames.append(tempname)

    path = list()
    pathname = list()
    getallpaths(G, source, target, path, paths, pathname, pathnames)
    return paths, pathnames

def predominate2(G, name, start):
    seq = []
    try:
        dic = nx.immediate_dominators(G, start)
        temp = name
        while temp != start:
            seq.insert(0, temp)
            temp = dic[temp]
    except:
        seq.append(name)
    return seq

def alter(dotflie) :
    filedate = ""
    with open(dotflie, "r") as f:
        for line in f:
            if "digraph" in line:
                line.replace("digraph", "graph")
            if "shape=record,label=" in line:
                line = re.sub(r'[|][{].*[}]', "", line)
                line = line.replace(":\"",":}\"")
            if "shape=record,label=" not in line and ":" in line:
                line = re.sub(re_dot, "", line)
            filedate += line
#    print(filedate)
    with open(dotflie, "w") as f:
        f.write(filedate)

def getcfgGraph(dotfile):
    node2line = {}
    G = nx.DiGraph()
    with open(dotfile, "r") as f:
        dotinfo = f.readlines()
    for line in dotinfo:
        try:
            if "shape=record,label=" in line:
                li = re.findall(re_bblabel, line)[0][:-1]    
                node = line.strip().split(" ")[0]
                node2line[node] = li
        except:
            print(line)
    # print(node2line)
    for line in dotinfo:
        if "->" in line:
            head, tail = line.strip()[:-1].split("->")
            head = head.strip()
            tail = tail.strip()
            try:
                G.add_edge(node2line[head], node2line[tail])
            except:
                pass
    return G




if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument ('-d', '--dot', type=str, required=True, help="Path to dot-file representing the graph.")
    parser.add_argument ('-t', '--targets', type=str, required=True, help="Path to file specifying Target nodes.")
    parser.add_argument ('-o', '--out', type=str, required=True, help="Path to output file containing distance for each node.")
    parser.add_argument ('-k', '--target', type=str, required=True)
    args = parser.parse_args ()
    
    print ("generate callgraph..." )
    G_callgraph = nx.DiGraph(nx.drawing.nx_pydot.read_dot(args.dot + "/callgraph.dot"))
    # print (nx.info(G_callgraph))

    with open(args.targets + "/fun2line.txt", "r") as f:
        for l in f.readlines():
            fun = l.strip().split("\t")[0]
            line = l.strip().split("\t")[1]
            fun2line[fun] = line

    with open(args.targets + "/call2line.txt", "r") as f:
        for l in f.readlines():
            try:
                call = l.strip().split("\t")[0]
                line = l.strip().split("\t")[1]
                call2line[call] = line
            except:
                pass

    with open(args.targets + "/ftargets.txt", "r") as f:
        for l in f.readlines():
            try:
                target = l.strip().split("\t")[0]
                funname = l.strip().split("\t")[1]
                if "main" == funname:
                    funname = prefix + funname
                dotname = "cfg." + funname + ".dot"
                filename = "dequence_" + target.strip().split(":")[1] + "---" + funname
                alter(args.dot + "/" + dotname)
                G = getcfgGraph(args.dot + "/" + dotname)
            # targetsfile[filename] = []
            # targetsfile[filename].extend(predominate1(G_callgraph, funname, "main"))
            # # print(G.nodes())
            # targetsfile[filename].extend(predominate2(G, target, fun2line[funname]))
            # print(targetsfile)
                if args.target == "nm-new":
                    args.target = "nm"
                prefix = args.target + ".c."
                paths, pathnames = getpath(G_callgraph, "main", funname)
                for pathname in pathnames:
                    pathname[0] = args.target + ".c.main"
                print(pathnames)
                print("-" * 15)
                cfgseq = predominate2(G, target, fun2line[funname])
                cfgseq.insert(0, fun2line[funname])
                k = 0
            
                for pathname in pathnames:
                    key = filename + str(k)
                    targetsfile[key] = []
                    for i in range(len(pathname) - 1):
                        dot = "cfg." + pathname[i] + ".dot"
                        alter(args.dot + "/" + dot)
                        Gtemp = getcfgGraph(args.dot + "/" + dotname)
                        seq = predominate2(Gtemp, call2line[pathname[i] + ":" + pathname[i + 1]], fun2line[pathname[i]])
                        seq.insert(0, fun2line[pathname[i]])
                    # print(seq)
                        targetsfile[key].extend(seq)
                    targetsfile[key].extend(cfgseq)
                # print(cfgseq)
                # print("-" * 20)
                    k = k + 1
                print(targetsfile)

            except:
                pass  
            # for path in paths:
            #     key = filename + str(k)
            #     targetsfile[key] = []
            #     print(path)
            #     targetsfile[key].extend(path)
            #     targetsfile[key].extend(cfgseq)
            #     k = k + 1
            #     print(cfgseq)
            # print(targetsfile)

    for key, value in targetsfile.items():
        with open(args.out + "/" + key, "w") as f:
            for v in value:
                f.write(v + "\n")
            
