# -*- coding: utf-8 -*-
name = "cueweb"

version = "1.4.11"

authors = ["Open Cue"]

description = "CueWeb is a web-based tool for managing and monitoring render jobs in the Open Cue system. It provides a user-friendly interface to interact with the Cue system, allowing users to submit, monitor, and manage their render jobs efficiently."

requires = ["python-3.11", "loguru"]

tools = ["cueweb"]

build_command = "python3 {root}/build.py {install}"

uuid = "repository.cueweb"


def commands():
    env.PATH.append("{root}/bin")
