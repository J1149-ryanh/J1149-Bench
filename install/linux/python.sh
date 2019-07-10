#!/bin/bash
echo $PATH
# Docker should be ran with sudo; this ensures that it is, at least with Pycharm.
eval "$(conda shell.bash hook)"
conda activate J1149-Bench
py=$(command -v python)
cd "$J1149_BENCH"
# If it's run in normal mode and the first param is the python file
if [ ${1: -3} == ".py" ] && grep -q "docker" "$1"; then
    sudo "$py" "$@"
# If it's run in debug mode and the ninth param is the python file
elif [[ $# -eq 9 ]]  && [ ${9: -3} == ".py" ] && grep -q "docker" "$9"; then
    sudo "$py" "$@"
else
	"$py" "$@"
fi
