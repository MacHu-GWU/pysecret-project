#!/bin/bash
# -*- coding: utf-8 -*-

dir_here="$( cd "$(dirname "$0")" ; pwd -P )"
dir_bin="$(dirname "${dir_here}")"
dir_project_root=$(dirname "${dir_bin}")

source ${dir_bin}/py/python-env.sh

print_colored_line $color_cyan "[DOING] create virtualenv for ${venv_name} at ${dir_venv} ..."
if [ ${use_pyenv} == "Y" ]; then
    pyenv virtualenv ${py_version} ${venv_name}
    ${bin_pip} install --upgrade pip
else
    virtualenv -p ${bin_global_python} ${dir_venv}
    ${bin_pip} install --upgrade pip
fi
