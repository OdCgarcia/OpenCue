#!/usr/bin/env python3

# Copyright (c) 2025. Od Studios, www.theodstudios.com, All rights reserved

import os
import os.path
import shutil
import subprocess
import sys
from typing import List

from loguru import logger


class TestError(Exception):
    pass


def _fix_rqd_imports(rqd_directory):
    """Fix import statements in RQD source files to use compiled_proto instead of opencue_proto."""
    logger.info("Fixing opencue_proto imports to use rqd.compiled_proto")

    # Files that need import fixes
    files_to_fix = ["rqcore.py", "rqmachine.py", "rqnetwork.py", "rqdservicers.py", "cuerqd.py"]

    for filename in files_to_fix:
        filepath = os.path.join(rqd_directory, filename)
        if os.path.exists(filepath):
            logger.info(f"Fixing imports in {filename}")

            with open(filepath, "r") as f:
                content = f.read()

            # Replace opencue_proto imports with compiled_proto imports
            # Handle both "import opencue_proto.X" and "from opencue_proto.X import Y"
            content = content.replace("import opencue_proto.", "import rqd.compiled_proto.")
            content = content.replace("from opencue_proto.", "from rqd.compiled_proto.")

            # Also handle cases where opencue_proto is used directly (like in class inheritance)
            content = content.replace("opencue_proto.", "rqd.compiled_proto.")

            with open(filepath, "w") as f:
                f.write(content)

            logger.info(f"Updated imports in {filename}")
        else:
            logger.warning(f"File not found: {filepath}")


def build(source_path: str, build_path: str, install_path: str, targets: List[str]) -> None:
    logger.info(f"Source Path -> {source_path}")
    logger.info(f"Build Path -> {build_path}")
    logger.info(f"Install Path -> {install_path}")
    logger.info(f"Targets -> {targets}")

    @logger.catch(exception=TestError, reraise=True)
    def _build():
        # Option 4 approach: Compile proto files directly
        proto_src_path = os.path.join(os.path.dirname(source_path), "proto", "src")
        compiled_proto_path = os.path.join(source_path, "rqd", "compiled_proto")

        if os.path.exists(proto_src_path):
            logger.info("Compiling proto files (Option 4 approach)")

            # Create compiled_proto directory
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

        # Copy source files to build directory (Option 4 approach - no pip needed)
        logger.info("Copying source files to build directory")
        rqd_src = os.path.join(source_path, "rqd")
        rqd_dest = os.path.join(build_path, "rqd")

        if os.path.exists(rqd_dest):
            shutil.rmtree(rqd_dest)

        shutil.copytree(rqd_src, rqd_dest)

        # Fix imports in RQD source files to use compiled_proto instead of opencue_proto
        logger.info("Fixing opencue_proto imports in RQD source files")
        _fix_rqd_imports(rqd_dest)

        # Create bin directory and rqd executable script
        bin_dir = os.path.join(build_path, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        rqd_exe = os.path.join(bin_dir, "rqd")

        # Get Python path from environment
        python_root = os.environ.get("REZ_PYTHON_ROOT")
        if python_root:
            python_path = os.path.join(python_root, "bin", "python3")
        else:
            python_path = sys.executable

        # Create executable script (equivalent to pyproject.toml [project.scripts])
        rqd_script = f"""#!{python_path}
# -*- coding: utf-8 -*-
import re
import sys
from rqd.__main__ import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\\.pyw|\\.exe)?$', '', sys.argv[0])
    sys.exit(main())
"""

        with open(rqd_exe, "w") as f:
            f.write(rqd_script)

        os.chmod(rqd_exe, 0o755)
        logger.info(f"Created rqd executable at {rqd_exe}")

    def _install():
        logger.info("Installing files and directories")

        # Install the rqd directory
        rqd_build = os.path.join(build_path, "rqd")
        rqd_install = os.path.join(install_path, "rqd")

        if os.path.exists(rqd_build):
            logger.info(f"Installing rqd from {rqd_build} to {rqd_install}")
            if os.path.exists(rqd_install):
                shutil.rmtree(rqd_install)
            shutil.copytree(rqd_build, rqd_install)
        else:
            raise TestError(f"RQD build directory not found: {rqd_build}")

        # Install the bin directory
        bin_build = os.path.join(build_path, "bin")
        bin_install = os.path.join(install_path, "bin")

        if os.path.exists(bin_build):
            logger.info(f"Installing bin from {bin_build} to {bin_install}")
            if os.path.exists(bin_install):
                shutil.rmtree(bin_install)
            shutil.copytree(bin_build, bin_install)
        else:
            raise TestError(f"Bin build directory not found: {bin_build}")

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
