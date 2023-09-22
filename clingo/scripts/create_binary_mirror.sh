#!/bin/bash

specs=$(${SPACK_CMD} find --format="/{hash}" clingo-bootstrap)
mkdir -p /home/spack/binary-mirror
${SPACK_CMD} buildcache push  -a -u -f /home/spack/binary-mirror ${specs}
