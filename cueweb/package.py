# -*- coding: utf-8 -*-

name = "cueweb"

version = "1.4.12"

authors = ["Open Cue"]

description = "CueWeb is a web-based tool for managing and monitoring render jobs in the Open Cue system. It provides a user-friendly interface to interact with the Cue system, allowing users to submit, monitor, and manage their render jobs efficiently."

requires = ["python-3.11", "loguru"]

tools = ["cueweb"]

build_command = "python3 {root}/build.py {install}"

uuid = "repository.cueweb"


def commands():
    import json
    import os

    # Load secrets from external JSON file
    secrets_file = "/od/.farm_web.json"
    secrets = {}
    if os.path.exists(secrets_file):
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
    env.PATH.append("{root}/bin")
    env.NEXT_JWT_SECRET = secrets.get("NEXT_JWT_SECRET", "default-jwt-secret")
    # NOTE: NEXT_PUBLIC_OPENCUE_ENDPOINT is overridden in build.py due to rez environment variable issues
    env.NEXT_PUBLIC_OPENCUE_ENDPOINT = "http://10.0.5.31:8448"
    env.NEXT_PUBLIC_URL = "http://localhost:3000"
    env.NEXTAUTH_SECRET = secrets.get("NEXTAUTH_SECRET", "default-nextauth-secret")
    env.NEXTAUTH_URL = "http://localhost:3000"

    # Authentication Configuration
    env.NEXT_PUBLIC_AUTH_PROVIDER = "google"
    env.GOOGLE_CLIENT_ID = secrets.get("GOOGLE_CLIENT_ID", "your-google-client-id")
    env.GOOGLE_CLIENT_SECRET = secrets.get("GOOGLE_CLIENT_SECRET", "your-google-client-secret")

    # Okta placeholders (required by config validation but not used for Google-only auth)
    env.NEXT_AUTH_OKTA_CLIENT_ID = "placeholder-okta-id"
    env.NEXT_AUTH_OKTA_ISSUER = "https://placeholder.okta.com"
    env.NEXT_AUTH_OKTA_CLIENT_SECRET = "placeholder-okta-secret"
