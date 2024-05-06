#!/bin/sh

# Cycle over all the Python interpreters in manylinux2014
# and install the corresponding clingo-bootstrap binary
for PYTHON in /opt/python/cp${1}*/bin/python; do
  # Install clingo using the current Python as an external
  # The Python version will be output to stdout
  ${PYTHON} spack/bin/spack python install_clingo.py
done
