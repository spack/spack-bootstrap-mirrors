import sys

import archspec.cpu
import spack.bootstrap.config
import spack.main

if sys.platform == "linux":
    CLINGO_BASE_SPEC = "clingo-bootstrap@spack +static_libstdcpp +optimized +ipo ~docs"
else:
    CLINGO_BASE_SPEC = "clingo-bootstrap@spack +optimized +ipo ~docs"

install = spack.main.SpackCommand("install")


with spack.bootstrap.config.spack_python_interpreter():
    msg = "Installing clingo-bootstrap with Python: {0}"
    print(msg.format(spack.bootstrap.config.spec_for_current_python()))
    install(f"{CLINGO_BASE_SPEC} target={archspec.cpu.host().family}")
