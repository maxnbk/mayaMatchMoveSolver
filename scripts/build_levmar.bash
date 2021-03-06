#!/usr/bin/env bash
# Builds the levmar shared library.

# Store the current working directory, to return to.
CWD=`pwd`

# Path to this script.
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# The root of this project.
PROJECT_ROOT=`readlink -f ${THIS_DIR}/..`

# The root of the project external directory.
ROOT=${THIS_DIR}/../external/
echo Package Root: ${ROOT}
cd ${ROOT}

INSTALL_DIR="${ROOT}/install/levmar"

# Extract LevMar
python "${THIS_DIR}/get_levmar.py" "${ROOT}/archives" "${ROOT}/working" "${ROOT}/patches"

# Build Library
mkdir -p build
cd build
rm -R *
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_DEMO=OFF \
    -DHAVE_LAPACK=0 \
    -DNEED_F2C=0 \
    -DLM_SNGL_PREC=0 \
    ../working/levmar-2.6
make clean
make all

# The CMake script with levmar does not not define an install process.
# So we copy the files manually
mkdir -p ${ROOT}/install/levmar/lib
mkdir -p ${ROOT}/install/levmar/include
cp ${ROOT}/build/liblevmar.so ${ROOT}/install/levmar/lib/
# cp ${ROOT}/build/levmar.a ${ROOT}/install/levmar/lib/
cp ${ROOT}/working/levmar-2.6/levmar.h ${ROOT}/install/levmar/include/

# Return back project root directory.
cd ${CWD}
