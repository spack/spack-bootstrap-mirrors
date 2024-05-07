"""Produce the clingo.json file associated with the mirror"""
import json
import glob
import hashlib
import os.path

import json

# Each entry in clingo.json has the following keys:
#
# "spec": root spec to be matched
# "hash": dag hash of the spec in the binary mirror
# "python": constraints on the python interpreter
# "sha256": SHA 256 sum of the binary tarball
# "compiler": compiler entry used to build the spec
#

# Dictionary that maps (OS, TARGET) to info for the spec
SPEC_INFO = {
    ('rhel5', 'x86_64'): {
        'spec': 'clingo-bootstrap%gcc platform=linux target=x86_64',
    },
    ('centos7', 'x86_64'): {
        'spec': 'clingo-bootstrap%gcc platform=linux target=x86_64',
    },
    ('centos7', 'aarch64'): {
        'spec': 'clingo-bootstrap%gcc platform=linux target=aarch64',
    },
    ('centos7', 'ppc64le'): {
        'spec': 'clingo-bootstrap%gcc platform=linux target=ppc64le',
    },
    ('monterey', 'x86_64'): {
        'spec': 'clingo-bootstrap%apple-clang platform=darwin target=x86_64',        
    },
    ('ventura', 'aarch64'): {
        'spec': 'clingo-bootstrap%apple-clang platform=darwin target=aarch64',        
    }
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

glob_expr = './build_cache/*.json'
spec_yaml_files = glob.glob(glob_expr)

mirror_info = []
for spec_json in spec_yaml_files:
    if "clingo" not in spec_json:
        continue

    # Get the raw data from spec.json
    with open(spec_json) as f:
        spec_yaml_data = json.load(f)['spec']['nodes']

    # Cycle through the specs in raw data. We are only interested 
    # in clingo bootstrap
    binary_data = {}
    for entry in spec_yaml_data:
        current_spec = entry['name']
        if current_spec not in ('clingo-bootstrap', 'python'):
            continue

        if current_spec == 'clingo-bootstrap':
            clingo_data = entry
            binary_data['clingo'] = clingo_data

        elif current_spec == 'python':
            python_data = entry
            binary_data['python'] = python_data
        
    assert 'clingo' in binary_data, 'entry "clingo" is required'
    assert 'python' in binary_data, 'entry "python" is required' 
    
    current_os = binary_data['clingo']['arch']['platform_os']
    current_target = binary_data['clingo']['arch']['target']
    
    compiler_name = binary_data['clingo']['compiler']['name']
    compiler_version = str(binary_data['clingo']['compiler']['version'])

    python_version = binary_data['python']['version']
    python_spec = 'python@{0}'.format(python_version)
    if python_version == '2.7':
        ucs4 = binary_data['python']['parameters']['ucs4']
        python_spec += '+ucs4' if ucs4 else '~ucs4'  

    current_hash = binary_data['clingo']['hash']
    mirror_entry = {
        "spec": SPEC_INFO[(current_os, current_target)]['spec'],
        "python": python_spec,
        "binaries": [
            ('clingo-bootstrap', current_hash, shas[current_hash])
        ],
    }
    mirror_info.append(mirror_entry)

mirror_info = sorted(mirror_info, key=lambda x: (x['spec'], x['python']))
with open('./clingo.json', 'w') as f:
    json.dump({'verified': mirror_info}, f, sort_keys=True, indent=2)
