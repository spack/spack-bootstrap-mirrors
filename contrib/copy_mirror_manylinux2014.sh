#!/bin/sh

for platform in amd64 arm64 ppc64le; do
    id="$(docker create --platform "linux/$platform" "${SPACK_MANYLINUX2014_TAG}")"
    mkdir "$platform"
    docker cp "$id:/root/binary-mirror" "$platform/binary-mirror"
    docker rm -v "$id"
done

# Unify the mirrors. This is required since the upload-artifacts action computes the common
# ancestor among different paths and starts from there instead of "merging" the copies
mkdir binary-mirror
rsync -a ./*/binary-mirror/ ./binary-mirror
