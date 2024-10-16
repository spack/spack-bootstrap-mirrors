"""Produce the clingo.json file associated with the mirror"""

import glob
import hashlib
import json
import os.path

# Each entry in patchelf.json has the following keys:
#
# "spec": root spec to be matched
# "binaries": list of objects, to be installed in order (each one has a "hash", "sha256" and "name" attribute)
# "python": constraints on the python interpreter
# "compiler": compiler entry used to build the spec
#

# Dictionary that maps (OS, TARGET) to info for the spec
SPEC_INFO = {
    ("centos7", "x86_64"): {
        "spec": "patchelf@0.13: %gcc platform=linux target=x86_64",
    },
    ("centos7", "aarch64"): {
        "spec": "patchelf@0.13: %gcc platform=linux target=aarch64",
    },
    ("centos7", "ppc64le"): {
        "spec": "patchelf@0.13: %gcc platform=linux target=ppc64le",
    },
}


def compiler_entry(name, version, os, target):
    return {
        "spec": "{0}@{1}".format(name, version),
        "paths": {
            "cc": "/dev/null",
            "cxx": "/dev/null",
            "f77": "/dev/null",
            "fc": "/dev/null",
        },
        "operating_system": "{0}".format(os),
        "target": "{0}".format(target),
        "modules": [],
    }


def sha256(path):
    fn = hashlib.sha256()
    with open(path, "rb") as f:
        fn.update(f.read())
    return fn.hexdigest()


def tarball_hash(path):
    filename = os.path.basename(path)
    filename = filename.replace(".spack", "")
    return filename.split("-")[-1]


tarballs = glob.glob("./build_cache/**/*.spack", recursive=True)
shas = {tarball_hash(tarball): sha256(tarball) for tarball in tarballs}
spec_yaml_files = glob.glob("./build_cache/*.json")

mirror_info = []
spec_yaml_dict = {}
for spec_yaml in spec_yaml_files:
    if "patchelf" not in spec_yaml:
        continue
    print(spec_yaml)
    # Get the raw data from spec.yaml
    with open(spec_yaml) as f:
        spec_yaml_data = json.load(f)["spec"]["nodes"]

    # Find the patchelf entry and store it somewhere
    binary_data = {}
    for entry in spec_yaml_data:
        if "patchelf" == entry["name"]:
            binary_data["patchelf"] = entry
    assert "patchelf" in binary_data

    current_os = binary_data["patchelf"]["arch"]["platform_os"]
    current_target = binary_data["patchelf"]["arch"]["target"]

    compiler_name = binary_data["patchelf"]["compiler"]["name"]
    compiler_version = str(binary_data["patchelf"]["compiler"]["version"])

    current_hash = binary_data["patchelf"]["hash"]
    binaries = [("patchelf", current_hash, shas[current_hash])]
    mirror_entry = {
        "spec": SPEC_INFO[(current_os, current_target)]["spec"],
        "binaries": binaries,
    }
    mirror_info.append(mirror_entry)

mirror_info = sorted(mirror_info, key=lambda x: x["spec"])
with open("./patchelf.json", "w") as f:
    json.dump({"verified": mirror_info}, f, sort_keys=True, indent=2)
