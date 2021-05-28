"""Produce the clingo.json file associated with the mirror"""
import json
import glob
import hashlib
import os.path

import ruamel.yaml

# Each entry in gnupg.json has the following keys:
#
# "spec": root spec to be matched
# "binaries": list of objects, to be installed in order (each one has a "hash", "sha256" and "name" attribute)
# "python": constraints on the python interpreter
# "compiler": compiler entry used to build the spec
#

# Dictionary that maps (OS, TARGET) to info for the spec
SPEC_INFO = {
    ('rhel5', 'x86_64'): {
        'spec': 'gnupg@2.3: %gcc platform=linux target=x86_64',
    },
    ('centos7', 'aarch64'): {
        'spec': 'gnupg@2.3: %gcc platform=linux target=aarch64',
    },
    ('centos7', 'ppc64le'): {
        'spec': 'gnupg@2.3: %gcc platform=linux target=ppc64le',
    },
    ('catalina', 'x86_64'): {
        'spec': 'gnupg@2.3: %apple-clang platform=darwin target=x86_64',        
    }
}

def compiler_entry(name, version, os, target):
    return {
        "spec": "{0}@{1}".format(name, version),
        "paths": {
          "cc": "/dev/null",
          "cxx": "/dev/null",
          "f77": "/dev/null",
          "fc": "/dev/null"
        },
        "operating_system": "{0}".format(os),
        "target": "{0}".format(target),
        "modules": []
    }

def sha256(path):
    fn = hashlib.sha256()
    with open(path, "rb") as f:
        fn.update(f.read())
    return fn.hexdigest()

def tarball_hash(path):
    filename = os.path.basename(path)
    filename = filename.replace('.spack', '')
    return filename.split('-')[-1]

shaglob_expr = './build_cache/**/*.spack'
tarballs = glob.glob(shaglob_expr, recursive=True)
shas = {tarball_hash(tarball): sha256(tarball) for tarball in tarballs}
print(shas)

glob_expr = './build_cache/*.yaml'
spec_yaml_files = glob.glob(glob_expr)

yaml = ruamel.yaml.YAML()
mirror_info = []
spec_yaml_dict = {}
for spec_yaml in spec_yaml_files:
    if 'gnupg' not in spec_yaml:
        continue
    
    # Get the raw data from spec.yaml
    with open(spec_yaml) as f:
        spec_yaml_data = yaml.load(f)['spec']
        
    # Find the GnuPG entry and store it somewhere
    binary_data = {}
    for entry in spec_yaml_data:
        if 'gnupg' in entry:
            binary_data['gnupg'] = entry['gnupg']

    # Cycle again through the specs and determine the order
    # of installation of dependencies        
    sorted_entries = []
    for entry in spec_yaml_data:
        spec_yaml_dict.update(entry)
        for key, item in entry.items():
            dependencies = item.get('dependencies', {})
            build_only = []
            for name, dep_info in dependencies.items():                
                if len(dep_info['type']) == 1 and 'build' in dep_info['type']:
                    build_only.append(name)

            for name in build_only:
                dependencies.pop(name)
            dep_tuple = len(dependencies), key
            print(dep_tuple)
            sorted_entries.append(dep_tuple)
            

    # Sort the entries by number of dependencies
    sorted_entries = [x for x in sorted_entries if x[1] in binary_data['gnupg']['dependencies']]
    sorted_entries.sort()

    binaries = []
    for ndeps, name in sorted_entries:
        current_hash = spec_yaml_dict[name]['hash']
        binaries.append(
            (name, current_hash, shas[current_hash])
        )
        
    assert 'gnupg' in binary_data, 'entry "gnupg" is required'
    
    current_os = binary_data['gnupg']['arch']['platform_os']
    current_target = binary_data['gnupg']['arch']['target']
    
    compiler_name = binary_data['gnupg']['compiler']['name']
    compiler_version = str(binary_data['gnupg']['compiler']['version'])

    current_hash = binary_data['gnupg']['hash']
    binaries.append(
        ('gnupg', current_hash, shas[current_hash])
    )
    mirror_entry = {
        "spec": SPEC_INFO[(current_os, current_target)]['spec'],
        #"hash": current_hash,
        #"sha256": shas[current_hash],
        "binaries": binaries,
        "compiler": compiler_entry(compiler_name, compiler_version, current_os, current_target) 
    }
    mirror_info.append(mirror_entry)

mirror_info = sorted(mirror_info, key=lambda x: x['spec'])
with open('./gnupg.json', 'w') as f:
    json.dump({'verified': mirror_info}, f, sort_keys=True, indent=2)
