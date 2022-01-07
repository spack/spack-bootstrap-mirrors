#!/usr/bin/env sh

id=$(docker create --platform linux/amd64 ghcr.io/alalazo/manylinux2014_mirrors:latest)
mkdir amd64
docker cp $id:/home/spack/binary-mirror amd64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/arm64 ghcr.io/alalazo/manylinux2014_mirrors:latest)
mkdir arm64
docker cp $id:/home/spack/binary-mirror arm64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/ppc64le ghcr.io/alalazo/manylinux2014_mirrors:latest)
mkdir ppc64le
docker cp $id:/home/spack/binary-mirror ppc64le/binary-mirror
docker rm -v $id

# Unify the mirrors. This is required since the upload-artifacts action
# computes the common ancestor among different paths and starts from there
# instead of "merging" the copies
mkdir binary-mirror
rsync -a ./amd64/binary-mirror/ ./binary-mirror
rsync -a ./arm64/binary-mirror/ ./binary-mirror
rsync -a ./ppc64le/binary-mirror/ ./binary-mirror
