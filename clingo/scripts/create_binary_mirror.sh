#!/bin/bash

specs=$(spack find --format="/{hash}" clingo-bootstrap)
mkdir -p /home/spack/binary-mirror
spack buildcache push  --unsigned --force /home/spack/binary-mirror ${specs}
