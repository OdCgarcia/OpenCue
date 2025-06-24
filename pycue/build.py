#!/usr/bin/env python3

# Copyright (c) 2025. Od Studios, www.theodstudios.com, All rights reserved

import os
import os.path
import pathlib
import shutil
import subprocess
import sys
from typing import List

from loguru import logger


class TestError(Exception):
    pass


def build(source_path: str, build_path: str, install_path: str, targets: List[str]) -> None:
    logger.info(f"Source Path -> {source_path}")
    logger.info(f"Build Path -> {build_path}")
    logger.info(f"Install Path -> {install_path}")
    logger.info(f"Targets -> {targets}")

    @logger.catch(exception=TestError, reraise=True)
    def _build():
        # Create python directory in build path
        python_build_dir = os.path.join(build_path)
        os.makedirs(python_build_dir, exist_ok=True)

        # Compile proto files directly (similar to rqd approach)
        proto_src_path = os.path.join(os.path.dirname(source_path), "proto", "src")
        compiled_proto_path = os.path.join(python_build_dir, "opencue_proto")

        if os.path.exists(proto_src_path):
            logger.info("Compiling proto files for pycue")

            # Create opencue_proto directory
            if os.path.exists(compiled_proto_path):
                shutil.rmtree(compiled_proto_path)
            os.makedirs(compiled_proto_path, exist_ok=True)

            # Get all .proto files
            proto_files = []
            for file in os.listdir(proto_src_path):
                if file.endswith(".proto"):
                    proto_files.append(file)

            if not proto_files:
                raise TestError("No .proto files found in proto source directory")

            logger.info(f"Found proto files: {proto_files}")

            # Compile proto files using grpc_tools.protoc
            try:
                cmd = [
                    sys.executable,
                    "-m",
                    "grpc_tools.protoc",
                    "-I=.",
                    f"--python_out={compiled_proto_path}",
                    f"--grpc_python_out={compiled_proto_path}",
                ] + proto_files

                logger.info(f"Running command: {' '.join(cmd)}")
                logger.info(f"Working directory: {proto_src_path}")

                result = subprocess.run(cmd, cwd=proto_src_path, check=True, capture_output=True, text=True)
                logger.info("Proto files compiled successfully")
                if result.stdout:
                    logger.info(f"stdout: {result.stdout}")
                if result.stderr:
                    logger.info(f"stderr: {result.stderr}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to compile proto files: {e}")
                logger.error(f"stdout: {e.stdout}")
                logger.error(f"stderr: {e.stderr}")
                raise TestError(f"Proto compilation failed: {e}")

            # Fix compiled proto imports using OpenCue's fix script
            fix_script_path = os.path.join(os.path.dirname(source_path), "proto", "fix_compiled_proto.py")
            if os.path.exists(fix_script_path):
                logger.info("Running fix_compiled_proto.py to fix imports")
                try:
                    subprocess.run(
                        [sys.executable, fix_script_path, compiled_proto_path],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    logger.info("Proto imports fixed successfully")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to fix proto imports: {e}")
                    logger.error(f"stdout: {e.stdout}")
                    logger.error(f"stderr: {e.stderr}")
                    raise TestError(f"Proto import fixing failed: {e}")
            else:
                logger.warning(f"fix_compiled_proto.py not found at {fix_script_path}")

            # Run 2to3 conversion on compiled proto files
            try:
                # Get all .py files in compiled_proto directory
                py_files = [f for f in os.listdir(compiled_proto_path) if f.endswith(".py")]
                if py_files:
                    logger.info(f"Running 2to3 on {len(py_files)} Python files")
                    subprocess.run(
                        ["2to3", "-w", "-n"] + py_files,
                        cwd=compiled_proto_path,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    logger.info("2to3 conversion completed")
                else:
                    logger.warning("No Python files found for 2to3 conversion")
            except subprocess.CalledProcessError as e:
                logger.warning(f"2to3 conversion failed or not needed: {e}")
            except FileNotFoundError:
                logger.warning("2to3 tool not found, skipping conversion")
        else:
            raise TestError(f"Proto source not found at {proto_src_path}")

        # Walk only one level of the source path
        _source_path = pathlib.Path(source_path)
        for path in _source_path.iterdir():
            logger.info(f"Processing: {path.name}")

            if path.name == "build":
                # Skip the build directory
                continue

            # Handle all other files/directories
            dest = os.path.join(python_build_dir, path.name)

            # Check if destination exists and remove it
            if os.path.exists(dest):
                logger.info(f"Removing existing: {dest}")
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                else:
                    os.remove(dest)

            # Copy the file or directory
            logger.info(f"Copying {path.name} to {dest}")
            if path.is_dir():
                shutil.copytree(str(path), dest)
            else:
                shutil.copy2(str(path), dest)

    def _install():
        logger.info("Installing files and directories")

        # Install the python directory
        python_build_dir = os.path.join(build_path)
        if os.path.exists(python_build_dir):
            python_install_dir = os.path.join(install_path)
            if os.path.exists(python_install_dir):
                shutil.rmtree(python_install_dir)

            logger.info(f"Copying from {python_build_dir} to {python_install_dir}")
            shutil.copytree(python_build_dir, python_install_dir)

    _build()

    if "install" in (targets or []):
        _install()


if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
