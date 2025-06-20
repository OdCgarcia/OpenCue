#!/usr/bin/env python3

# Copyright (c) 2025. Od Studios, www.theodstudios.com, All rights reserved

import os
import os.path
import shutil
import subprocess
import sys
from typing import List

from loguru import logger


class BuildError(Exception):
    pass


def build(source_path: str, build_path: str, install_path: str, targets: List[str]) -> None:
    logger.info(f"Source Path -> {source_path}")
    logger.info(f"Build Path -> {build_path}")
    logger.info(f"Install Path -> {install_path}")
    logger.info(f"Targets -> {targets}")

    # Define what gets copied to the final package
    build_artifacts = ["bin", ".next", "package.json", "package-lock.json", "next.config.js", "public"]

    def _build():
        logger.info("Building CueWeb using npm")

        # Log environment info for debugging
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"PATH: {os.environ.get('PATH', 'Not set')}")

        # First, copy source files to build directory for npm operations
        logger.info("Copying source files to build directory")
        # Note: build_path already exists and contains Rez files, so we copy into it

        # Copy source files into the existing build directory
        for item in os.listdir(source_path):
            # Skip hidden files and directories that start with '.'
            if item.startswith("."):
                continue

            src_item = os.path.join(source_path, item)
            dest_item = os.path.join(build_path, item)

            # Skip patterns we don't want
            skip_patterns = ["node_modules", "__pycache__", "build", ".git", ".env", ".next"]

            if any(item.startswith(pattern) or item == pattern for pattern in skip_patterns):
                logger.info(f"Skipping {item}")
                continue

            if os.path.isdir(src_item):
                if os.path.exists(dest_item):
                    shutil.rmtree(dest_item)
                shutil.copytree(src_item, dest_item)
            else:
                shutil.copy2(src_item, dest_item)

            logger.debug(f"Copied {item} to build directory")

        logger.info(f"Source files copied to build directory: {build_path}")

        # Check if npm is available
        try:
            result = subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True, cwd=build_path)
            logger.info(f"npm is available (version: {result.stdout.strip()})")
        except subprocess.CalledProcessError as e:
            logger.error(f"npm check failed with exit code {e.returncode}")
            if e.stderr:
                logger.error(f"npm stderr: {e.stderr}")
            raise BuildError(f"npm is not working properly. Exit code: {e.returncode}")
        except FileNotFoundError:
            raise BuildError("npm is not available. Please install Node.js and npm to build CueWeb.")

        # Set up build environment
        build_env = os.environ.copy()
        build_env.update(
            {
                "NODE_ENV": "production",
                "NEXT_TELEMETRY_DISABLED": "1",
                "SENTRYCLI_SKIP_DOWNLOAD": "1",
                # Set default build-time environment variables
                "NEXTAUTH_URL": "http://localhost:3000",
                "NEXTAUTH_SECRET": "build-time-secret",
                "NEXT_JWT_SECRET": "build-time-jwt-secret",
                "NEXT_AUTH_OKTA_CLIENT_ID": "build-time-okta-id",
                "NEXT_AUTH_OKTA_ISSUER": "https://build-time.okta.com",
                "NEXT_AUTH_OKTA_CLIENT_SECRET": "build-time-okta-secret",
                "NEXT_PUBLIC_URL": "http://localhost:3000",
                "NEXT_PUBLIC_OPENCUE_ENDPOINT": "http://localhost:8080",
                "NEXT_PUBLIC_AUTH_PROVIDER": "google,okta,github",
            }
        )

        # Install dependencies
        logger.info("Installing npm dependencies")
        try:
            cmd = ["npm", "ci", "--production=false"]
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=build_path, check=True, capture_output=True, text=True, env=build_env)
            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            if e.stdout:
                logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
            raise BuildError(f"npm install failed with return code {e.returncode}")

        # Build the Next.js application
        logger.info("Building Next.js application")
        try:
            cmd = ["npm", "run", "build"]
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, cwd=build_path, check=True, capture_output=True, text=True, env=build_env)
            logger.info("Next.js build completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Next.js application: {e}")
            if e.stdout:
                logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"stderr: {e.stderr}")
            raise BuildError(f"npm build failed with return code {e.returncode}")

        # Create executable script
        _create_executable()

        # Remove unnecessary files from build directory (keep only what we need for runtime)
        _cleanup_build_directory()

    def _create_executable():
        """Create the cueweb executable script"""
        bin_dir = os.path.join(build_path, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        cueweb_exe = os.path.join(bin_dir, "cueweb")

        script_content = """#!/bin/bash
# CueWeb startup script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUEWEB_ROOT="$(dirname "$SCRIPT_DIR")"

# Set environment variables
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Default values
CUEWEB_PORT=${CUEWEB_PORT:-3000}
CUEWEB_HOST=${CUEWEB_HOST:-0.0.0.0}

# Parse command line arguments
COMMAND="start"
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            COMMAND="dev"
            export NODE_ENV=development
            shift ;;
        --port=*) CUEWEB_PORT="${1#*=}"; shift ;;
        --port) CUEWEB_PORT="$2"; shift 2 ;;
        --host=*) CUEWEB_HOST="${1#*=}"; shift ;;
        --host) CUEWEB_HOST="$2"; shift 2 ;;
        --help|-h)
            echo "CueWeb - Web-based OpenCue management interface"
            echo "Usage: cueweb [options]"
            echo "Options:"
            echo "  --dev, --development   Run in development mode"
            echo "  --port=PORT           Port to run on (default: 3000)"
            echo "  --host=HOST           Host to bind to (default: 0.0.0.0)"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Required Environment Variables:"
            echo "  NEXT_PUBLIC_OPENCUE_ENDPOINT   OpenCue REST API endpoint"
            echo "  NEXT_JWT_SECRET                JWT secret for API authentication"
            exit 0 ;;
        *) echo "Unknown option: $1"; echo "Use --help for usage."; exit 1 ;;
    esac
done

# Check required environment variables
if [ -z "$NEXT_PUBLIC_OPENCUE_ENDPOINT" ] || [ -z "$NEXT_JWT_SECRET" ]; then
    echo "Error: Required environment variables not set:"
    echo "  NEXT_PUBLIC_OPENCUE_ENDPOINT"
    echo "  NEXT_JWT_SECRET" 
    exit 1
fi

# Set the port for Next.js
export PORT="$CUEWEB_PORT"

echo "Starting CueWeb on ${CUEWEB_HOST}:${CUEWEB_PORT}"
echo "CueWeb root: $CUEWEB_ROOT"

# Change to CueWeb directory and start the application
cd "$CUEWEB_ROOT"
exec npm run "$COMMAND" -- --port "$CUEWEB_PORT" --hostname "$CUEWEB_HOST"
"""

        with open(cueweb_exe, "w") as f:
            f.write(script_content)

        os.chmod(cueweb_exe, 0o755)
        logger.info(f"Created cueweb executable at {cueweb_exe}")

    def _cleanup_build_directory():
        """Remove unnecessary files from build directory, keep only runtime artifacts"""
        cleanup_patterns = [
            "src",
            "app/__tests__",
            "jest",
            "jest.config.js",
            ".eslintrc.json",
            ".prettierrc.json",
            ".prettierignore",
            "README.md",
            "tailwind.config.js",
            "tailwind.config.ts",
            "tsconfig.json",
            "postcss.config.js",
            "components.json",
            "Dockerfile",
            "sentry.*.config.ts",
            "build.py",
            "interface_screenshots",
        ]

        for pattern in cleanup_patterns:
            path = os.path.join(build_path, pattern)
            if os.path.exists(path):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                logger.info(f"Removed {pattern} from build directory")

    def _install():
        """Install only the necessary runtime artifacts"""
        for artifact in build_artifacts:
            src = os.path.join(build_path, artifact)
            dest = os.path.join(install_path, artifact)

            if not os.path.exists(src):
                logger.warning(f"Artifact {artifact} not found in build directory, skipping")
                continue

            # Remove existing destination (handle both files and directories)
            if os.path.exists(dest):
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                else:
                    os.remove(dest)

            logger.info(f"Installing: {src} to {dest}")
            if os.path.isdir(src):
                shutil.copytree(src, dest)
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)

        # Ensure executable permissions for bin files
        # bin_dir = os.path.join(install_path, "bin")
        # if os.path.exists(bin_dir):
        #     for file_name in os.listdir(bin_dir):
        #         filepath = os.path.join(bin_dir, file_name)
        #         os.chmod(filepath, 0o755)

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
