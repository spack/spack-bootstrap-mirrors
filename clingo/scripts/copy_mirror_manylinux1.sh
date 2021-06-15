#!/usr/bin/env sh

id=$(docker create ghcr.io/alalazo/manylinux1_mirrors_x86_64:latest)
docker cp $id:/home/spack/binary-mirror binary-mirror
docker rm -v $id
