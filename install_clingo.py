import spack.bootstrap
import spack.main

install = spack.main.SpackCommand('install')

with spack.bootstrap.spack_python_interpreter():
    msg = 'Installing clingo-bootstrap with Python: {0}'
    print(msg.format(spack.bootstrap.spec_for_current_python()))
    install('clingo-bootstrap@spack target=x86_64')

