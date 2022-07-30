# LeoFuzz使用方法和验证方法

## 1.通过静态分析获得程序的cfg和cg，并生成对应的增强目标序列
```shell
LEOFUZZ="/afl-2.52b"
cp -r mjs mjs-issues
cd /mjs-issues; git checkout d6c06a6
mv mjs mjs-bin
mkdir obj-leofuzz; mkdir obj-leofuzz/temp
export SUBJECT=$PWD; export TMP_DIR=$PWD/obj-leofuzz/temp
export CC=$LEOFUZZ/afl-clang-fast; export CXX=$LEOFUZZ/afl-clang-fast++
export LDFLAGS=-lpthread 
export ADDITIONAL="-outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
echo $'mjs.c:12523' > $TMP_DIR/targets.txt
$CC -DMJS_MAIN mjs.c $ADDITIONAL -ldl -g -o mjs
cat $TMP_DIR/fun2line.txt | sort | uniq > $TMP_DIR/fun2line2.txt && mv $TMP_DIR/fun2line2.txt $TMP_DIR/fun2line.txt
/scripts/genSequence.sh $SUBJECT $TMP_DIR mjs
cd /mjs-issues;
mkdir temp; cd temp
mkdir in out
echo "" > in/in
cp -r ../obj-leofuzz/temp/Leofuzztemp ./
/scripts/changeseq.py -s /mjs-issues/temp/Leofuzztemp
```

### 2.对被测程序进行插桩，包括目标序列基本块的插桩和其他基本块的插桩，并计算目标序列优先级
```shell
cd /mjs-issues
export SUBJECT=$PWD; export TMP_DIR=$PWD/temp
export ADDITIONAL="-targets=$TMP_DIR/Leofuzztemp -outdir=$TMP_DIR"
$CC -DMJS_MAIN mjs.c $ADDITIONAL -ldl -g -o mjs
/scripts/getBBseq.py -b  $TMP_DIR
$LEOFUZZ/scripts/sequence.py $TMP_DIR
/scripts/getPriority.py -p $TMP_DIR
```

## 3.对被测程序正常编译供混合执行器的使用
```shell
IN="$TMP_DIR/in"
OUT="$TMP_DIR/out"
cd /mjs-issues/
mkdir obj-qsym; cd obj-qsym;
gcc -DMJS_MAIN ../mjs.c -ldl -g -o mjs
```

## 4.模糊测试和混合执行的启动(注意QSYM是否存在)
```shell
if [[ ! -f /qsym/bin/run_qsym_afl.py ]] ; then
    echo 'QSYM is not there, aborting.'
    exit
fi
-f <fil
cd ..
$LEOFUZZ/afl-fuzz -m none -c 5m -p $TMP_DIR/runtimeseq.txt -P $TMP_DIR/priority.txt  -M afl-master -i $IN -o $OUT -- $SUBJECT/mjs -f @@ &

$LEOFUZZ/afl-fuzz -m none -c 5m -p $TMP_DIR/runtimeseq.txt -P $TMP_DIR/priority.txt -S afl-slave -i $IN -o $OUT -- $SUBJECT/mjs -f @@ &

while [ ! -f $OUT/afl-slave/fuzzer_stats ]
do
        sleep 2
        echo "no fuzzer_stats sleep 2"
done
/qsym/bin/run_qsym_afl.py -a afl-slave -o $OUT -n qsym -- /obj-qsym/mjs -f @@ &
```



