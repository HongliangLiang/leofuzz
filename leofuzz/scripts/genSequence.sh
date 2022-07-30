#!/bin/bash
if [ $# -lt 2 ]; then
  echo "Usage: $0 <binaries-directory> <temporary-directory> [fuzzer-name]"
  echo ""
  exit 1
fi

BINARIES=$(readlink -e $1)
TMPDIR=$(readlink -e $2)
fuzzer=""

if [ $# -eq 3 ]; then
  fuzzer=$(find $BINARIES -name "$3.0.0.*.bc" | rev | cut -d. -f5- | rev)
  if [ $(echo "$fuzzer" | wc -l) -ne 1 ]; then
    echo "Couldn't find bytecode for fuzzer $3 in folder $BINARIES."
    exit 1
  fi
fi

#SANITY CHECKS
if [ -z "$BINARIES" ]; then echo "Couldn't find binaries folder ($1)."; exit 1; fi
if ! [ -d "$BINARIES" ]; then echo "No directory: $BINARIES."; exit 1; fi
if [ -z "$TMPDIR" ]; then echo "Couldn't find temporary directory ($3)."; exit 1; fi

binaries=$(find $BINARIES -name "*.0.0.*.bc" | rev | cut -d. -f5- | rev)
if [ -z "$binaries" ]; then echo "Couldn't find any binaries in folder $BINARIES."; exit; fi

if [ -z $(which python) ] && [ -z $(which python3) ]; then echo "Please install Python"; exit 1; fi
#if python -c "import pydotplus"; then echo "Install python package: pydotplus (sudo pip install pydotplus)"; exit 1; fi
#if python -c "import pydotplus; import networkx"; then echo "Install python package: networkx (sudo pip install networkx)"; exit 1; fi

cd $TMPDIR/dot-files

if [ -z "$fuzzer" ]; then
  for binary in $(echo "$binaries"); do

    echo " Constructing CG for $binary.."
    while ! opt -dot-callgraph $binary.0.0.*.bc >/dev/null; do
      echo -e "\e[93;1m[!]\e[0m Could not generate call graph. Repeating.."
    done

      #Remove repeated lines and rename
    awk '!a[$0]++' callgraph.dot > callgraph.$(basename $binary).dot
    rm callgraph.dot
  done

  #Integrate several call graphs into one
  echo $(ls callgraph.*)
  /scripts/merge_callgraphs.py -o callgraph.dot $(ls callgraph.*)
  echo " Integrating several call graphs into one."

else
  echo " Constructing CG for $fuzzer.."
  echo "-------------------------------------------------------------------------------------------------------------------------------"
  while ! opt -dot-callgraph $fuzzer.0.0.*.bc >/dev/null; do
    echo -e "\e[93;1m[!]\e[0m Could not generate call graph. Repeating.."
  done

    #Remove repeated lines and rename
  awk '!a[$0]++' callgraph.dot > callgraph.1.dot
  mv callgraph.1.dot callgraph.dot

fi
echo "Get merge line for fun2line..."
/scripts/mergeline.py -i $TMPDIR/fun2line.txt
cat $TMPDIR/fun2line.txt | sort  > $TMPDIR/fun2line2.txt && mv $TMPDIR/fun2line2.txt $TMPDIR/fun2line.txt

echo "Start get target sequence..."
cd $TMPDIR 
mkdir Leofuzztemp
/scripts/Sequence.py -t $TMPDIR -o $TMPDIR/Leofuzztemp -d $TMPDIR/dot-files -k $3
echo "Target sequence is getting"
