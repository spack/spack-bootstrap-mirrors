#!/usr/bin/env spack-python
"""Produce a bootstrap json file for a selected package"""

import glob
import hashlib
import json
import os
import sys

import spack.deptypes as dt
import spack.spec
import spack.traverse

# Each entry in clingo.json has the following keys:
#
# "spec": root spec to be matched
# "binaries": list of tuples (pkg name, dag hash, sha256 sum)


def sha256(path):
    fn = hashlib.sha256()
    with open(path, "rb") as f:
        fn.update(f.read())
    return fn.hexdigest()


def tarball_hash(path: str):
    # extract hash from /path/to/<...>-<hash>.spack
    name, _ = os.path.splitext(os.path.basename(path))
    return name.split("-")[-1]


def run(pkg: str, deps=dt.NONE, python: bool = False):
    name = "clingo-bootstrap" if pkg == "clingo" else pkg
    shas = {
        tarball_hash(tarball): sha256(tarball)
        for tarball in glob.glob("./build_cache/**/*.spack", recursive=True)
    }

    specs = [
        spack.spec.Spec.from_specfile(f) for f in glob.glob("./build_cache/*.json") if name in f
    ]

    assert len(specs) > 0, f"No specs found for {name}"

    fmt = "{name}{@version}{%compiler.name} platform={platform} target={target}"

    if python:
        fmt_spec = lambda s: f"{s.format(fmt)} ^python@{s.dependencies('python')[0].version}"
    else:
        fmt_spec = lambda s: s.format(fmt)

    mirror_info = [
        {
            "spec": fmt_spec(s),
            "binaries": [
                (s.name, s.dag_hash(), shas[s.dag_hash()])
                for s in reversed(list(s.traverse(order="topo", deptype=deps)))
                if not s.external
            ],
        }
        for s in specs
    ]

    # sort as strings, cause Spec instances with deps don't sort properly
    mirror_info.sort(key=lambda x: x["spec"])

    with open(f"./{pkg}.json", "w") as f:
        json.dump({"verified": mirror_info}, f, sort_keys=True, indent=2)


if __name__ == "__main__":
    assert len(sys.argv) == 2, f"Usage: {sys.argv[0]} <clingo|gnupg|patchelf>"
    pkg = sys.argv[1]
    # unfortunately we refer to clingo-bootstrap by alias "clingo"
    assert pkg in ("clingo", "gnupg", "patchelf")
    run(
        pkg,
        # clingo is special: statically links libstdc++ and other deps are loaded by interpreter
        deps=dt.NONE if pkg == "clingo" else dt.LINK | dt.RUN,
        python=pkg == "clingo",
    )
