#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker build -t roman_tools . && \
  docker run \
    --mount type=bind,src=$DIR/notebooks,dst=/home/jovyan/notebooks \
    -p 127.0.0.1:8888:8888 \
    roman_tools
