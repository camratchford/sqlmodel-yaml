#!/bin/bash
THIS_DIR="$(dirname "$(realpath "$0")")"

pushd "$THIS_DIR"

if [ ! -f "$(which mkdocs)" ]; then
    echo "mkdocs not found in PATH"
    echo "You probably need to activate the venv and run 'pip install .[development]'"
    exit 1
fi

pushd "../docs/"

mkdocs build

popd > /dev/null
popd > /dev/null