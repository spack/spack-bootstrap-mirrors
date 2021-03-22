#!/bin/bash

# Cycle over all the Python interpreters in manylinux1
# and install the corresponding clingo-bootstrap binary
for PYTHON in /opt/python/*/bin/python; do
  # Force reinstall a cmake for this Python interpreter
  ${PYTHON} -m pip -qq install --force-reinstall cmake

  # Install clingo using the current Python as an external
  # The Python version will be output to stdout
  ${PYTHON} spack/bin/spack python install_clingo.py

  # Remove cmake for the next interpreter to work
  ${PYTHON} -m pip -qq uninstall -y cmake
done

# Clean pip cache
/opt/python/cp39-cp39/bin/python -m pip cache purge

# Create a binary mirror
/bin/bash create_binary_mirror.sh

