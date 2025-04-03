#!/bin/bash

function find_llama_path() {
    # echo "@i@ --> find dir: ${0}"
    this_script_dir=$( dirname -- "$0"; )
    pwd_dir=$( pwd; )

    if [ "${this_script_dir:0:1}" = "/" ]
    then
        # echo "get absolute path ${this_script_dir}" > /dev/tty
        LLAMA_PATH=${this_script_dir}"/../"
    else
        # echo "get relative path ${this_script_dir}" > /dev/tty
        LLAMA_PATH=${pwd_dir}"/"${this_script_dir}"/../"
    fi
    echo "${LLAMA_PATH}"
}

LLAMA_PATH=$( find_llama_path )
cd ${LLAMA_PATH}

mkdir -p texas/build/bin
mkdir -p texas/tools
mkdir -p texas/images/270p

## copy libopenblas64-dev libraries
cp /usr/lib/aarch64-linux-gnu/libopenblas.so    texas/build/bin
cp /usr/lib/aarch64-linux-gnu/libopenblas64.so  texas/build/bin
cp build/bin/*.so                   texas/build/bin
cp build/bin/llama-qwen2vl-server   texas/build/bin
cp tools/run_qwen2_server.sh        texas/tools
cp tools/*.py                       texas/tools
cp -r images/270p                   texas/images