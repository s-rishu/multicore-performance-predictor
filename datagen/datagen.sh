#!/bin/sh

ctx_dir=./ctx_config
x86_dir=./x86_config
mem_dir=./mem_config
tmp=./tmp
out=./out

simMemHardware() 
{
    for k in ./mem_config/*.ini
    do
        echo "Memory: $k configuration env..."
        $m2s --x86-sim detailed --x86-config $3 --ctx-config $tmp/$1 &>> ($out/$1)
        wait
    done
}

simMultiHardware() 
{
    for j in ./x86_config/*.ini
    do
        echo "Hardware: $j configuration env..."
        simMemHardware $1 $2 $j
    done
}

runMultiProg()
{
    mkdir $tmp

    configs=`ls $ctx_dir/* | xargs -n 1 basename`

    for input in $configs
    do
        
        echo "Program: $input benchmarking..."

        for j in 1 2 4 8 16 32 64
        do
            echo "Threads count: $j total threads..."
            cp -rf $ctx_dir/$input $tmp/$input
            sed -i "s|%NTHREADS|$j|g" $tmp/$input
	        cat $tmp/$input
            simMultiHardware $input
        done
    done

    echo "Cleaning up temp files..."
    rm -rf $tmp
}

runMultiProg

