name = "rqd"

version = "1.4.12"

authors = ["Open Cue"]

description = """
    RQD (Render Queue Daemon) for OpenCue.
    A render farm management system.
    """

variants = [["platform-linux", "arch-x86_64", "os-Rocky-9"]]

build_requires = ["cmake-3", "python-3.11"]

requires = ["python-3.11", "loguru"]

tools = ["rqd"]

uuid = "repository.rqd"

build_command = "python3 {root}/build.py {install}"


def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.prepend("{root}")
    env.PYTHONPATH.prepend("{root}/rqd/compiled_proto")
    env.CUEBOT_HOSTNAME.set("odfarm01")
