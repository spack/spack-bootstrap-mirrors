#!/bin/bash

specs=$(${SPACK_CMD} find --format="/{hash}" clingo-bootstrap)
mkdir -p /home/spack/binary-mirror
${SPACK_CMD} buildcache create -d /home/spack/binary-mirror -a -u -f ${specs}
