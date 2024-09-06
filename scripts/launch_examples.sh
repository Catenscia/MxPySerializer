#!/bin/bash
set -e

# Initialize Conda
source ~/anaconda3/etc/profile.d/conda.sh

# build
rm dist/*
python -m build

# create a new env
ENV_NAME="mxpyserializer_example_env"
conda create -n $ENV_NAME python=3.10 -y
conda activate $ENV_NAME

# install project and providers
pip install dist/*whl
pip install multiversx_sdk_network_providers

# launch integration tests
cd examples
python onedex.py

# remove env
conda deactivate
conda env remove -n $ENV_NAME -y