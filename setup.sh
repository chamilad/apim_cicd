#!/bin/bash

set -e

command -v python2 >/dev/null 2>&1 || {
    echo >&2 "Please install Python 2.7 and add it \$PATH."
    exit 1
}

py_version=$(python2 --version 2>&1 | awk '{print $2}')
if [[ $py_version != 2.7* ]]; then
    print_crossmark
    echo >&2 "Python required version \"2.7.x\" doesn't match found version \"${py_version}\"."
    exit 1
fi

command -v pip2 >/dev/null 2>&1 || {
    echo >&2 "Please install Python Pip 2.7 and add it to \$PATH."
    exit 1
}

if [ ! -d venv ]; then
    echo "Creating virtual environment..."
    pip2 install --user virtualenv
    virtualenv -p $(which python2.7) venv
    echo
fi

echo "Installing dependencies..."
source venv/bin/activate
pip2 install -r requirements.txt
echo

echo "done"
echo

bash check_requirements.sh
echo

deactivate

echo "Run \"source venv/bin/activate\" to enable the virtual environment. Run \"deactivate\" to exit from the virtual environment."
echo "For more information on virtual environments, go to https://virtualenv.pypa.io/en/latest/"
exit 0
