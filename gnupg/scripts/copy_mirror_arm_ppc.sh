#!/usr/bin/env sh

id=$(docker create --platform linux/arm64 ghcr.io/alalazo/gnupg_manylinux2014:latest)
mkdir arm64
docker cp $id:/home/spack/binary-mirror arm64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/ppc64le ghcr.io/alalazo/gnupg_manylinux2014:latest)
mkdir ppc64le
docker cp $id:/home/spack/binary-mirror ppc64le/binary-mirror
docker rm -v $id

# Unify the two mirrors. This is required since the upload-artifacts action
# computes the common ancestore among different paths and starts from there
# instead of "merging" the copies
mkdir binary-mirror
rsync -a ./arm64/binary-mirror/ ./binary-mirror
rsync -a ./ppc64le/binary-mirror/ ./binary-mirror
