#!/bin/sh

simMemHardware() 
{
    for k in {1..2}
    do
        echo "Memory $k.ini configuration env..."
        $m2s --x86-sim detailed --mem-config ./mem-config/$k.ini --x86-config ./x86-config/$2.ini --ctx-config ./ctx-config/$1.ini
        wait
    done
}

simMultiHardware() 
{
    for j in {1..2}
    do
        echo "Hardware $j.ini configuration env...\n"
        simMemHardware $1 $j
    done
}

runMultiProg()
{
    for i in {1..2}
    do
        echo "Program $i benchmarking...\n"
        simMultiHardware $i
    done
}

runMultiProg

