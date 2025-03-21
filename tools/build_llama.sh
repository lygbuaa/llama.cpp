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

mkdir ${LLAMA_PATH}/build
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DGGML_RPC=ON
cmake --build build --config Release