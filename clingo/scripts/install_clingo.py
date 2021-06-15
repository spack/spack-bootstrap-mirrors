import archspec.cpu

import spack.bootstrap
import spack.main

install = spack.main.SpackCommand('install')

with spack.bootstrap.spack_python_interpreter():
    msg = 'Installing clingo-bootstrap with Python: {0}'
    print(msg.format(spack.bootstrap.spec_for_current_python()))
    clingo_str = 'clingo-bootstrap@spack target={0}'.format(
        str(archspec.cpu.host().family)
    )
    install(clingo_str)
