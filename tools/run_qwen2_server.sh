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
LIB_LLAMA_PATH=${LLAMA_PATH}/build/bin
export LD_LIBRARY_PATH=${LIB_LLAMA_PATH}:$LD_LIBRARY_PATH

VL_MODEL_PATH=${LLAMA_PATH}/../vlm_models/qwen2/Qwen2-VL-7B-Instruct-IQ2_M.gguf
PROJ_MODEL_PATH=${LLAMA_PATH}/../vlm_models/qwen2/mmproj-Qwen2-VL-7B-Instruct-Q4_K.gguf
IMG_PATH=${LLAMA_PATH}/../vlm_models/image/bridge_640_360.jpg
PROMPT="图片是哪个地方?"
HOST_IP=127.0.0.1
HOST_PORT=10001
TEMPERATURE=0.0

${LLAMA_PATH}/build/bin/llama-qwen2vl-server \
-m ${VL_MODEL_PATH} \
--mmproj ${PROJ_MODEL_PATH} \
--temp ${TEMPERATURE} \
--image ${IMG_PATH} \
--host ${HOST_IP} \
--port ${HOST_PORT} \
-p ${PROMPT}
