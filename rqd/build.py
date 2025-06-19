#!/usr/bin/env python3

# Copyright (c) 2025. Od Studios, www.theodstudios.com, All rights reserved

import os
import os.path
import shutil
import subprocess
import sys
import venv
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
        # Create virtual environment in build directory
        venv_path = os.path.join(build_path, "OpenCue-venv")

        # Clean up any existing virtual environment before starting
        if os.path.exists(venv_path):
            logger.info(f"Removing existing virtual environment at {venv_path}")
            shutil.rmtree(venv_path)

        logger.info(f"Creating virtual environment at {venv_path}")
        venv.create(venv_path, with_pip=True)

        # Get python and pip paths from the virtual environment
        python_exe = os.path.join(venv_path, "bin", "python")
        pip_exe = os.path.join(venv_path, "bin", "pip")

        logger.info(f"Using Python: {python_exe}")
        logger.info(f"Using pip: {pip_exe}")

        # Install proto package from parent directory
        proto_path = os.path.join(os.path.dirname(source_path), "proto")
        if os.path.exists(proto_path):
            logger.info(f"Installing proto package from {proto_path}")
            try:
                subprocess.run([pip_exe, "install", proto_path], check=True, capture_output=True, text=True)
                logger.info("Proto package installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install proto package: {e}")
                logger.error(f"stdout: {e.stdout}")
                logger.error(f"stderr: {e.stderr}")
                raise TestError(f"Proto package installation failed: {e}")
        else:
            logger.warning(f"Proto package not found at {proto_path}, skipping...")

        # Install rqd package from source
        logger.info(f"Installing rqd package from {source_path}")
        try:
            subprocess.run([pip_exe, "install", source_path], check=True, capture_output=True, text=True)
            logger.info("RQD package installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install rqd package: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise TestError(f"RQD package installation failed: {e}")

        # Copy installed packages to build directory
        site_packages_src = os.path.join(venv_path, "lib", "python3.11", "site-packages")
        site_packages_dest = os.path.join(build_path, "lib", "python3.11", "site-packages")

        if not os.path.exists(site_packages_src):
            raise TestError(f"Site-packages directory not found: {site_packages_src}")

        logger.info(f"Copying site-packages from {site_packages_src} to {site_packages_dest}")
        if os.path.exists(site_packages_dest):
            shutil.rmtree(site_packages_dest)

        os.makedirs(os.path.dirname(site_packages_dest), exist_ok=True)
        shutil.copytree(site_packages_src, site_packages_dest)

        # Copy rqd executable from venv to build/bin
        venv_bin_path = os.path.join(venv_path, "bin", "rqd")
        build_bin_dir = os.path.join(build_path, "bin")
        build_rqd_exe = os.path.join(build_bin_dir, "rqd")

        if os.path.exists(venv_bin_path):
            logger.info(f"Copying rqd executable from {venv_bin_path} to {build_rqd_exe}")
            os.makedirs(build_bin_dir, exist_ok=True)
            shutil.copy2(venv_bin_path, build_rqd_exe)

            # Update the shebang to use the environment's Python
            logger.info("Updating rqd executable shebang")

            # Construct Python path from Rez environment variables
            python_root = os.environ.get("REZ_PYTHON_ROOT")
            if python_root:
                python_path = os.path.join(python_root, "bin", "python3")
                logger.info(f"Using Python path from REZ_PYTHON_ROOT: {python_path}")
            else:
                # Fallback to current executable if Rez variables not available
                python_path = sys.executable
                logger.info(f"REZ_PYTHON_ROOT not found, using current executable: {python_path}")

            with open(build_rqd_exe, "r") as f:
                content = f.read()

            # Replace the shebang line
            lines = content.split("\n")
            if lines[0].startswith("#!"):
                lines[0] = f"#!{python_path}"
                logger.info(f"Updated shebang to use environment Python: {python_path}")
            else:
                logger.warning("No shebang found in rqd executable")

            # Write the updated content back
            with open(build_rqd_exe, "w") as f:
                f.write("\n".join(lines))

            # Make sure the executable is actually executable
            os.chmod(build_rqd_exe, 0o755)
        else:
            logger.warning(f"rqd executable not found at {venv_bin_path}")

        # Clean up virtual environment
        logger.info("Cleaning up virtual environment")
        if os.path.exists(venv_path):
            shutil.rmtree(venv_path)

    def _install():
        logger.info("Installing files and directories")

        # Install the Python site-packages to the install directory
        site_packages_build = os.path.join(build_path, "lib", "python3.11", "site-packages")
        site_packages_install = os.path.join(install_path, "lib", "python3.11", "site-packages")

        if os.path.exists(site_packages_build):
            logger.info(f"Installing site-packages from {site_packages_build} to {site_packages_install}")
            if os.path.exists(site_packages_install):
                shutil.rmtree(site_packages_install)

            os.makedirs(os.path.dirname(site_packages_install), exist_ok=True)
            shutil.copytree(site_packages_build, site_packages_install)
        else:
            logger.warning(f"Site-packages build directory not found: {site_packages_build}")

        # Install the bin directory
        bin_build_dir = os.path.join(build_path, "bin")
        bin_install_dir = os.path.join(install_path, "bin")

        if os.path.exists(bin_build_dir):
            logger.info(f"Installing bin directory from {bin_build_dir} to {bin_install_dir}")
            if os.path.exists(bin_install_dir):
                shutil.rmtree(bin_install_dir)

            shutil.copytree(bin_build_dir, bin_install_dir)
        else:
            logger.warning(f"Bin build directory not found: {bin_build_dir}")

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
