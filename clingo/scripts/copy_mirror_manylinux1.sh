#!/usr/bin/env sh

id=$(docker create ghcr.io/alalazo/manylinux1_mirrors:latest)
docker cp $id:/home/spack/binary-mirror binary-mirror
docker rm -v $id
