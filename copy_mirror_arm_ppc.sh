#!/usr/bin/env sh

id=$(docker create --platform linux/arm64 ghcr.io/alalazo/manylinux2014_mirrors:latest)
mkdir arm64
docker cp $id:/home/spack/binary-mirror arm64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/ppc64le ghcr.io/alalazo/manylinux2014_mirrors:latest)
mkdir ppc64le
docker cp $id:/home/spack/binary-mirror ppc64le/binary-mirror
docker rm -v $id
