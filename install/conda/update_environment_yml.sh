#!/bin/bash
conda activate J1149-Bench
rm environment.yml
rm requirements.txt
conda env export > environment.yml
conda list -e > requirements.txt