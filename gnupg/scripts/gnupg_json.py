"""Produce the gnupg.json file associated with the mirror"""

import glob
import hashlib
import json
import os.path

import spack.spec
import spack.traverse

# Each entry in gnupg.json has the following keys:
#
# "spec": root spec to be matched
# "binaries": list of objects, to be installed in order (each one has a "hash", "sha256" and "name" attribute)
# "python": constraints on the python interpreter
# "compiler": compiler entry used to build the spec
#

# Dictionary that maps (OS, TARGET) to info for the spec
SPEC_INFO = {
    ("centos7", "x86_64"): {"spec": "gnupg@2.3: %gcc platform=linux target=x86_64"},
    ("centos7", "aarch64"): {"spec": "gnupg@2.3: %gcc platform=linux target=aarch64"},
    ("centos7", "ppc64le"): {"spec": "gnupg@2.3: %gcc platform=linux target=ppc64le"},
    ("monterey", "x86_64"): {"spec": "gnupg@2.3: %apple-clang platform=darwin target=x86_64"},
    ("sonoma", "aarch64"): {"spec": "gnupg@2.3: %apple-clang platform=darwin target=aarch64"},
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


shaglob_expr = "./build_cache/**/*.spack"
tarballs = glob.glob(shaglob_expr, recursive=True)
shas = {tarball_hash(tarball): sha256(tarball) for tarball in tarballs}

glob_expr = "./build_cache/*.json"
spec_json_files = glob.glob(glob_expr)

mirror_info = []
spec_json_dict = {}
for spec_json in spec_json_files:
    if "gnupg" not in spec_json:
        continue

    s = spack.spec.Spec.from_specfile(spec_json)
    binaries = []
    for edge in reversed(
        spack.traverse.traverse_edges_topo([s], direction="children", deptype=("link", "run"))
    ):
        if edge.spec.external:
            continue
        node = edge.spec
        binaries.append((node.name, node.dag_hash(), shas[node.dag_hash()]))

    # Get the raw data from spec.json
    with open(spec_json) as f:
        spec_json_data = json.load(f)["spec"]["nodes"]

    # Find the GnuPG entry and store it somewhere
    binary_data = {}
    for entry in spec_json_data:
        if "gnupg" == entry["name"]:
            binary_data["gnupg"] = entry
    assert "gnupg" in binary_data

    assert "gnupg" in binary_data, 'entry "gnupg" is required'

    current_os = binary_data["gnupg"]["arch"]["platform_os"]
    current_target = binary_data["gnupg"]["arch"]["target"]

    # If the target is not generic, like x86_64 etc. it's a fully fledged object
    if not isinstance(current_target, str):
        current_target = current_target["name"]

    current_hash = binary_data["gnupg"]["hash"]
    mirror_entry = {"spec": SPEC_INFO[(current_os, current_target)]["spec"], "binaries": binaries}
    mirror_info.append(mirror_entry)

mirror_info = sorted(mirror_info, key=lambda x: x["spec"])
with open("./gnupg.json", "w") as f:
    json.dump({"verified": mirror_info}, f, sort_keys=True, indent=2)
