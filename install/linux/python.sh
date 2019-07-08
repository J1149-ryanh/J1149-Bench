#!/bin/bash
# Docker should be ran with sudo; this ensures that it is.
eval "$(conda shell.bash hook)"
conda activate J1149-Bench
py=$(command -v python)
cd "$J1149_BENCH"
pwd
if [ ${1: -3} == ".py" ] && grep -q "docker" "$1"; then
	sudo "$py" "$@"
else
	sudo "$py" "$@"
fi
