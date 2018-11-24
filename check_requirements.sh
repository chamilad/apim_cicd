#!/usr/bin/env bash

# Prints a check mark (✔) and terminates the line
#
print_checkmark() {
    echo -en $'\e[1m \u2714\e[0m'
    echo
}

# Print a cross mark (❌) and terminates the line
#
print_crossmark() {
    echo -en $'\e[1;31m \u2718\e[0m'
    echo
}

echo "Checking prerequisites..."
echo

echo -n "Python 2.7: "
command -v python >/dev/null 2>&1 || {
    print_crossmark
    echo >&2 "Python cannot be found. Aborting..."
    exit 1
}

py_version=$(python --version 2>&1 | awk '{print $2}')
if [[ $py_version != 2.7* ]]; then
    print_crossmark
    echo >&2 "Python version is not 2.7. Aborting..."
    exit 1
fi
print_checkmark

echo -n "Virtual Env: "
if [[ -z "$VIRTUAL_ENV" ]]; then
    print_crossmark
    echo >&2 "Not in a virtual env. It is advised to use a Python Virtual Environment to contain dependencies."
    echo >&2 "Create virtual environment by running setup.sh"
    exit 1
fi
print_checkmark

echo -n "Python Libs: "
pip freeze | grep requests > /dev/null 2>&1
if [ $? == 1 ]; then
    print_crossmark
    echo >&2 "One or more Python libraries are missing. Please install packages from requirements.txt or run setup.sh"
    exit 1
fi

pip freeze | grep urllib3 > /dev/null 2>&1
if [ $? == 1 ]; then
    print_crossmark
    echo >&2 "One or more Python libraries are missing. Please install packages from requirements.txt or run setup.sh"
    exit 1
fi
print_checkmark
