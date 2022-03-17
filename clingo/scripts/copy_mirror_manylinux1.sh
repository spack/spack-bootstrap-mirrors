#!/usr/bin/env sh

id=$(docker create ${SPACK_MANYLINUX1_TAG})
docker cp $id:/home/spack/binary-mirror binary-mirror
docker rm -v $id
