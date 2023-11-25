#!/bin/sh

ctx_dir=./ctx_config
x86_dir=../configgen/configs/x86_configs
mem_dir=../configgen/configs/mem_configs
tmp=./tmp
out=./out

simMemHardware() 
{
    memconfigs=`ls $mem_dir/$2/* | xargs -n 1 basename`
    for i in $memconfigs
    do
        j="${i%.*}"
        echo "Memory: $i configuration env..."
        $m2s --x86-sim detailed --x86-config $x86_dir/$2/$3.ini --mem-config $mem_dir/$2/$j.ini --ctx-config $tmp/$1.ini &>> $out/$1v$2_$3_$j.ini
        wait
    done
}

simMultiHardware() 
{
    folders=`ls -d -- $x86_dir/*/ | xargs -n 1 basename`
    for f in $folders
    do
	x86configs=`ls $x86_dir/$f/* | xargs -n 1 basename`
    	for i in $x86configs
    	do
            j="${i%.*}"
	    echo "Hardware: $i configuration env..."
    	    simMemHardware $1 $f $j
        done
    done
}

runMultiProg()
{
    mkdir $tmp

    configs=`ls $ctx_dir/* | xargs -n 1 basename`

    for input in $configs
    do
        
        echo "Program: $input benchmarking..."
        filename="${input%.*}"

        for j in 1 2 4 8 16 32 64
        do
            echo "Threads count: $j total threads..."
            cp -rf $ctx_dir/$input $tmp/$input
            sed -i "s|%NTHREADS|$j|g" $tmp/$input
	        cat $tmp/$input
            simMultiHardware $filename
        done
    done

    echo "Cleaning up temp files..."
    rm -rf $tmp
}

runMultiProg

