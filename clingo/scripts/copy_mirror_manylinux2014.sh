#!/usr/bin/env sh

id=$(docker create --platform linux/amd64 ${SPACK_MANYLINUX2014_TAG})
mkdir amd64
docker cp $id:/root/binary-mirror amd64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/arm64 ${SPACK_MANYLINUX2014_TAG})
mkdir arm64
docker cp $id:/root/binary-mirror arm64/binary-mirror
docker rm -v $id

id=$(docker create --platform linux/ppc64le ${SPACK_MANYLINUX2014_TAG})
mkdir ppc64le
docker cp $id:/root/binary-mirror ppc64le/binary-mirror
docker rm -v $id

# Unify the mirrors. This is required since the upload-artifacts action
# computes the common ancestor among different paths and starts from there
# instead of "merging" the copies
mkdir binary-mirror
rsync -a ./amd64/binary-mirror/ ./binary-mirror
rsync -a ./arm64/binary-mirror/ ./binary-mirror
rsync -a ./ppc64le/binary-mirror/ ./binary-mirror
