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

**The purpose of this repository is to define workflows that generate
binary packages suitable for bootstrapping Spack on most architectures**.
For completeness we report a summary of Spack requirements below:

Name | Supported Versions | System Requirement | Requirement Reason
--- | -------------------|---------------------|--------------------
Python | 3.6-3.11 | Yes | Interpreter for Spack
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
`linux` | `centos7` | `GCC 10.2.1`| `x86_64` | 3.6-3.11
`linux` | `centos7` | `GCC 10.2.1`| `aarch64` | 3.6-3.11
`linux` | `centos7` | `GCC 10.2.1`| `ppc64le` | 3.6-3.11
`darwin`| `MacOS 10.13` or later | `Apple Clang 13.0.0` | `x86_64` | 3.6-3.11
`darwin`| `MacOS 10.13` or later | `Apple Clang 13.1.6` | `aarch64` | 3.6-3.11

## Github Actions Workflows

All the `linux` workflows make use of a slightly customized
[manylinux2014](https://github.com/spack/manylinux) image. The customization is minimal
and amounts to building multi-arch images with the same name
on Github Actions.

### `clingo` specific caveats

To avoid having runtime dependencies on `libstdc++.so`, `clingo` is
linked against a static version of the runtime library.

### `GnuPG` specific caveats

On `darwin` `GnuPG` had to be built with `--disable-nls --without-libintl-prefix` to avoid having binary requirements on 
the system `libintl` installed in the CI environment.
