import archspec.cpu
import spack.bootstrap.config
import spack.main

install = spack.main.SpackCommand("install")

with spack.bootstrap.config.spack_python_interpreter():
    print(
        f"Installing clingo-bootstrap with Python: "
        f"{spack.bootstrap.config.spec_for_current_python()}"
    )
    clingo_str = (
        f"clingo-bootstrap@spack +optimized ~docs target={archspec.cpu.host().family}"
    )
    install(clingo_str)
