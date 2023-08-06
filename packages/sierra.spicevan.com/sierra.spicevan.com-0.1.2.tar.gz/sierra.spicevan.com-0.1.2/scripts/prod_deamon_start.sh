#!/usr/bin/env bash

port=$1
virtual_env=$2
project_root=$3

# Assumes there is a virtual env called 'pyr' where pyramid deps 
# are installed.
source ~/.virtualenvs/${virtual_env}/bin/activate

pserve --daemon --pid-file=${project_root}/pserve_${port}.pid ${project_root}/production.ini http_port=${port}
