#!/usr/bin/env python3

# Copyright (c) 2025. Od Studios, www.theodstudios.com, All rights reserved

import os
import os.path
import pathlib
import shutil
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

        # Create bin directory and cueadmin script
        bin_dir = os.path.join(python_build_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        
        # Create cueadmin executable script
        cueadmin_script = os.path.join(bin_dir, "cueadmin")
        with open(cueadmin_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
import sys
import os

# Add the package root to Python path
package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, package_root)

from cueadmin.__main__ import main

if __name__ == '__main__':
    main()
""")
        
        # Make the script executable
        os.chmod(cueadmin_script, 0o755)
        logger.info(f"Created executable script: {cueadmin_script}")

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
