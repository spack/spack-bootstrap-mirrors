#!/usr/bin/env spack-python
"""Produce a bootstrap json file for a selected package"""

import sys
import glob
import json
import gzip
from pathlib import Path
from typing import List, Dict

import spack.deptypes as dt
import spack.spec


def generate_json(pkg: str, deps=dt.NONE, python: bool = False) -> None:
    """
    Generate a bootstrap JSON file for the specified package.

    Args:
        pkg: Package name to generate bootstrap file for
        deps: Dependency types to include
        python: Whether to reformat Python version in spec format
    """
    # clingo-bootstrap is a special case where the pkg name doesn't
    # match what we expect as the output json filename and CI/CD stack
    name = "clingo-bootstrap" if pkg == "clingo" else pkg

    # Find all manifest files in the v3 binary cache
    matches = glob.glob(
        f"./{pkg}_binary_mirror*/v3/manifests/spec/*/*.spec.manifest.json"
    )

    shas: Dict[str, str] = {}
    specs: List[spack.spec.Spec] = []

    for manifest_path in matches:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        spec_sha = None
        install_sha = None

        for manifest_obj in manifest.get("data"):
            media_type = manifest_obj.get("mediaType")
            if media_type == "application/vnd.spack.spec.v5+json":
                spec_sha = manifest_obj.get("checksum")

            elif media_type == "application/vnd.spack.install.v2.tar+gzip":
                install_sha = manifest_obj.get("checksum")

        if not (spec_sha and install_sha):
            print("Warning: unable to find spec and install checksums in manifest:")
            print(f"\n  {manifest_path}\n")
            continue

        # Extract cache base path from manifest path
        base_path = Path(manifest_path).parents[4]

        blob_path = base_path / "blobs" / "sha256" / spec_sha[:2] / spec_sha
        try:
            with gzip.open(blob_path) as f:
                spec = spack.spec.Spec.from_dict(json.load(f))

        except (IOError, ValueError, json.JSONDecodeError) as e:
            print(f"Error loading spec from {blob_path}: {e}")
            continue

        shas[spec.dag_hash()] = install_sha
        if spec.name == name:
            specs.append(spec)

    if not specs:
        raise ValueError(f"No specs found for {pkg}")

    fmt = "{name}{@version} platform={platform} target={target} {%compiler.name}"

    # Define format function based on whether Python version should be included
    if python:

        def fmt_spec(s):
            return f"{s.format(fmt)} ^python@{s.dependencies('python')[0].version}"
    else:

        def fmt_spec(s):
            return s.format(fmt)

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

    # Sort as strings, cause Spec instances with deps don't sort properly
    mirror_info.sort(key=lambda x: x["spec"])

    # Write output JSON file
    with open(f"./{pkg}.json", "w") as f:
        json.dump({"verified": mirror_info}, f, sort_keys=True, indent=2)


def main() -> None:
    """Parse command line arguments and run generation."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <clingo|gnupg|patchelf>")
        sys.exit(1)

    # Valid bootstrap package options
    # unfortunately we refer to clingo-bootstrap by alias "clingo"
    pkgs = ("clingo", "gnupg", "patchelf")

    pkg = sys.argv[1]
    if pkg not in pkgs:
        print(f"Error: {sys.argv[1]} is not one of {pkgs}")
        sys.exit(1)

    generate_json(
        pkg,
        # clingo is special: statically links libstdc++ and other deps are loaded by interpreter
        deps=dt.NONE if pkg == "clingo" else dt.LINK | dt.RUN,
        python=(pkg == "clingo"),
    )


if __name__ == "__main__":
    main()
