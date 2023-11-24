#!/bin/sh

simMemHardware() 
{
    for k in ./mem_config/*.ini
    do
        echo "Memory: $k configuration env..."
        $m2s --x86-sim detailed --mem-config $k --x86-config $2 --ctx-config $1
        wait
    done
}

simMultiHardware() 
{
    for j in ./x86_config/*.ini
    do
        echo "Hardware: $j configuration env..."
        simMemHardware $1 $j
    done
}

runMultiProg()
{
    for i in ./ctx_config/*.ini
    do
        echo "Program: $i benchmarking..."
        for j in {1..16}
        do
            echo "Threads count: $j total threads..."
            sed -i "s|%NTHREADS|$j|g" $i
            simMultiHardware $i
        done
    done
}

runMultiProg

