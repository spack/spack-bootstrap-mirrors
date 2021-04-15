#!/bin/bash

specs=$(spack find --format="/{hash}" clingo-bootstrap)
mkdir -p /home/spack/binary-mirror
spack buildcache create -d /home/spack/binary-mirror -a -u -f ${specs}
