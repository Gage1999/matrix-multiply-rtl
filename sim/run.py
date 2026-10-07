from pathlib import Path
import sys

from cocotb_tools.runner import get_runner

project = Path(__file__).resolve().parents[1]
build_dir = project / "sim" / "build"

sys.path.insert(0, str(project / "tb"))

runner = get_runner("verilator")

runner.build(
    sources=[project / "rtl" / "matvec4x4.sv"],
    hdl_toplevel="matvec4x4",
    build_dir=build_dir,
    build_args=["--Wall"],
    timescale=("1ns", "1ps"),
    waves=True,
)

runner.test(
    hdl_toplevel="matvec4x4",
    test_module="matvec_test",
    test_dir=build_dir,
    waves=True,
)