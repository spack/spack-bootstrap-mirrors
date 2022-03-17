# Spack Bootstrap Mirrors

This repository contains several Github Action workflows that are used
to generate binaries to bootstrap
[Spack](https://github.com/spack/spack).
Stable binary artifacts are tagged and released.

## Purpose of this repository

Spack has some minimum requirements to work correctly. Most of them are
currently _system requirements_ i.e. they are assumed to be present on
the machines where Spack is run. 
This is usually the case for common software found on `linux` systems,
such as the `patch` or `tar` executables.
A few less common, but critical, dependencies are
instead bootstrapped by Spack if not present on the system.
These are currently:

1. `clingo`: needed to concretize specs
2. `GnuPG`: needed to sign and verify binaries
3. `patchelf`: needed to relocate binaries on `linux`

Besides `patchelf`, which will always be bootstrapped from sources both
`clingo` and `GnuPG` will preferably be bootstrapped from binaries.
**The purpose of this repository is to define workflows that generate
binary packages suitable for bootstrapping Spack on most architectures**.
For completeness we report a summary of Spack requirements below:

Name | Supported Versions | System Requirement | Requirement Reason
--- | -------------------|---------------------|--------------------
Python | 2.7,3.5-3.10 | Yes | Interpreter for Spack
C/C++ compilers | - | Yes | Building software
GNU make | - | Yes | Building software
patch | - | Yes | Building software
curl | - | Yes | Fetching archives
tar   | - | Yes | Extract/create archives
gzip  | - | Yes | Archive compression
unzip | - | Yes | Archive compression
bzip2 | - | Yes | Archive compression
xz   | - | Yes | Archive compression
zstd  | - | Yes | Archive compression
file  | - |  Yes | Binary packages
patchelf  | 0.13 or later |  No | Binary packages
GnuPG  | 2.1 or later | No | Binary packages
clingo | 5.5 | No | Concretization
git | - | Yes | Software repositories
hg | - | Yes | Software repositories
svn | - | Yes | Software repositories

## Supported platforms

A few different toolchains have been used to produce binaries depending
on the target platform and architecture. Choices have been mainly driven
by compatibility with the [manylinux](https://github.com/pypa/manylinux) project.

Platform | OS | Compiler Toolchain | Architecture | Python
---------|----|--------------------|--------------|-------
`linux` | `rhel5` | `GCC 9.3.0`| `x86_64` | 2.7,3.5
`linux` | `centos7` | `GCC 10.2.1`| `x86_64` | 3.6-3.10
`linux` | `centos7` | `GCC 10.2.1`| `aarch64` | 3.6-3.10
`linux` | `centos7` | `GCC 10.2.1`| `ppc64le` | 3.6-3.10
`darwin`| `MacOS 10.13` or later | `Apple Clang 12.0.0` | `x86_64` | 3.5-3.10

The `rhel5` choice corresponds to `manylinux1` and is used to generate binaries to
bootstrap unmaintained Python versions (i.e. 2.7 and 3.5) on `x86_64` architectures, 
`centos7` is instead due to `manylinux2014`
and used on `x86_64`, `aarch64` and `ppc64le` to bootstrap Python versions in the 3.6-3.10 range
The choice of the compiler toolchain is determined
by the necessity to support `C++14` for `clingo`. `GCC 9.3.0` has
been built with Spack on top of the system compiler present on
`rhel5` (`GCC 4.8.2`). All the dependencies that are not a Python extensions are
bootstrapped on `centos7` using `gcc@10.2.1` when the platform is `linux`.

## Github Actions Workflows

All the `linux` workflows make use, as a starting point, of a
slightly customized version of either the
[manylinux1](https://github.com/spack/manylinux1-static-libs)
image or of the
[manylinux2014](https://github.com/spack/manylinux) image. The customization is minimal
and amounts to avoid removing `libpython.a` in the final image, since
this library is needed by `CMake` to build `clingo`. For a thorough
explanation on why this library is missing upstream in the `manylinux`
project you can read [this issue](https://github.com/pypa/manylinux/issues/255) and the references therein.

Since Github Action doesn't provide runners for `aarch64` or `ppc64le`
architectures, the binaries for those have been built using
[Docker buildx](https://docs.docker.com/buildx/working-with-buildx/).
This ultimately emulates the architectures using
[QEMU](https://www.qemu.org)
which on the one hand permits to build artifacts seamlessly,
but on the other results in very slow builds that for `clingo` exceed the 6hrs granted by Github.
**Because of this at the moment the `ppc64le` and `aarch64le` binaries have been generated on a local 
machine and pushed to ghcr.io**.

### `clingo` specific caveats

To avoid having runtime dependencies on `libstdc++.so`, `clingo` is
linked against a static version of the runtime library.

### `GnuPG` specific caveats

On `darwin` `GnuPG` had to be built with `--disable-nls --without-libintl-prefix` to avoid having binary requirements on 
the system `libintl` installed in the CI environment.
