#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

conan profile new --detect default
conan profile update env.Python_EXECUTABLE=$Python_EXECUTABLE default
conan profile update env.Python_INCLUDE_DIR=$Python_INCLUDE_DIR default
conan profile update env.Python_LIBRARY_RELEASE=$Python_LIBRARY_RELEASE default
conan profile update options.boost:python_version=3.7 default

python build.py
