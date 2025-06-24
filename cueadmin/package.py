name = "cueadmin"

version = "1.4.11"

authors = ["Open Cue"]

description = """
    CueAdmin commandline client for OpenCue administration.
    """

build_requires = ["python-3.11", "loguru"]

requires = [
    "python-3.11",
    "pycue-1.4.11",
    "pyoutline-1.4.11",
]

tools = ["cueadmin"]

uuid = "repository.cueadmin"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
