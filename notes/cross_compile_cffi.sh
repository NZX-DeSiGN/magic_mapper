#!/bin/bash

# ChatGPT query: Write a bash script that cross compiles the Python CFFI module in a buildroot environment.

# Note that this script assumes that the Buildroot environment and the CFFI source code have already been set up and configured.
# The script should be executed from the Buildroot environment. The environment setup script, output/host/opt/environment-setup-${TARGET_ARCH},
# should also be available in the Buildroot environment.


# Set the path to the Buildroot environment
BR_DIR="/path/to/buildroot"

# Set the path to the CFFI source code
CFFI_SRC_DIR="/path/to/cffi/src"

# Set the target architecture for cross-compilation
TARGET_ARCH="arm"

# Set the Python version for cross-compilation
PYTHON_VERSION="3.9"

# Set the installation directory for the cross-compiled module
INSTALL_DIR="${BR_DIR}/output/host/usr/local/lib/python${PYTHON_VERSION}/site-packages"

# Enter the Buildroot environment
cd $BR_DIR
source output/host/opt/environment-setup-${TARGET_ARCH}

# Enter the CFFI source directory
cd $CFFI_SRC_DIR

# Cross-compile the CFFI module
python${PYTHON_VERSION} setup.py build_ext --inplace --use-double-check
python${PYTHON_VERSION} setup.py install --prefix=$INSTALL_DIR

# Exit the Buildroot environment
cd -
