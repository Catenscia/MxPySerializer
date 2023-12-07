#!/bin/bash
set -e

# Initialize Conda
source ~/anaconda3/etc/profile.d/conda.sh

# build
rm dist/*
python -m build

# create a new env
ENV_NAME="mxpyserializer_integration_test_env"
conda create -n $ENV_NAME python=3.10 -y
conda activate $ENV_NAME

# install project
pip install dist/*whl
pip install -r requirements-dev.txt

# launch integration tests
cd integration_tests
python -m pytest tests

# remove env
conda deactivate
conda env remove -n $ENV_NAME -y