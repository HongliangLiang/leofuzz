#!/usr/bin/env python3
import sys
import os


myfiles=[]
def search_file(filepath):
	for root,dirs,files in os.walk(filepath):
		for name in files:
			ff=os.path.join(root,name)
			if os.path.isfile(ff):
				if "BBdequence_" in os.path.split(ff)[1]:
					myfiles.append(ff)

if __name__=="__main__":
	filepath=sys.argv[1]
	search_file(filepath)
	seqfilecount=0
	if len(filepath)>=1:
		with open(filepath+"/runtimeseq.txt", 'w') as rt:
			with open(filepath+"/BBtargets.txt", "w") as bbt:
				targets=set()
				for ff in myfiles:
					with open(ff,'r') as f:
						wrlocs=[]
						preloc=0
						for line in f.readlines():
							ll=line.strip().split(",")
							loc=int(ll[0])
							flag=int(ll[1])
							if flag==1:
								if loc==preloc:
									continue
								wrlocs.append(str(loc))
								preloc=loc
					if len(wrlocs)>=1:
						rt.write("#"+str(seqfilecount)+":"+ff+"\n")
						for lloc in wrlocs:
							rt.write(lloc+"\n")
							target=ff.split('_')
							targets.add(target[-2]+":"+target[-1]+"\n")	
					f.close()
					seqfilecount=seqfilecount+1
				rt.write("#\n")
				for target in targets:
					bbt.write(target)
			bbt.close()
		rt.close()
