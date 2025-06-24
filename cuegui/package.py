name = "cuegui"

version = "1.4.11"

authors = ["Open Cue"]

description = """
    GUI for Open Cue.
    """

build_requires = ["cmake-3", "python-3.11", "PySide6-6+<7"]

requires = [
    "python-3.11",
    "pyoutline-1.4.11",
    "pycue-1.4.11",
    "PySide6-6+<7",
    "cuebot-1.4.11",
    "QtPy-2+<3",
    "grpcio_tools-1+<2",
    "future-1+<2",
    "PyYAML-6+<7",
    "six-1+<2",
    "loguru",
    "NodeGraphQtPy-0.6+<1",
]

tools = ["cuegui"]

uuid = "repository.cuegui"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
