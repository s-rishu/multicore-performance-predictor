#!/bin/sh

runMultiProg()
{
    echo "Running $1.ini with default configurations...\n"
    $m2s --x86-sim detailed --mem-config ./mem_config/1.ini --x86-config .x86_config/1.ini --ctx-config $1
}

runMultiProg("5.ini")

