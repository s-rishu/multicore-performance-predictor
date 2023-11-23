#!/bin/sh

runMultiProg()
{
    echo "Running $1.ini with default configurations...\n"
    $m2s --x86-sim detailed --ctx-config ./ctx_config/$1
    wait
}

runMultiProg "6.ini"

