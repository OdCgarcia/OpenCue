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
    env.PATH.append("{root}/bin")
    env.NEXT_JWT_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJuYW1lIjoiVGVzdCBVc2VyIiwiaWF0IjoxNzUxMDcwODIwLCJleHAiOjE3NTExNTcyMjB9.Xu0h_a0Yb_TWq_823dNwQCDnE5Eza6dp66-f-1xqTsQ"
    # NOTE: NEXT_PUBLIC_OPENCUE_ENDPOINT is overridden in build.py due to rez environment variable issues
    env.NEXT_PUBLIC_OPENCUE_ENDPOINT = "http://10.0.5.31:8448"
    env.NEXT_PUBLIC_URL = "http://localhost:3000"
    env.NEXTAUTH_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.nextauth.secret.for.cueweb.production"
    env.NEXTAUTH_URL = "http://localhost:3000"

    # Authentication Configuration
    env.NEXT_PUBLIC_AUTH_PROVIDER = "google"
    env.GOOGLE_CLIENT_ID = "184586801947-t0j901l73t3p1ggakk7cq6fvmj63duq6.apps.googleusercontent.com"
    env.GOOGLE_CLIENT_SECRET = "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"

    # Okta placeholders (required by config validation but not used for Google-only auth)
    env.NEXT_AUTH_OKTA_CLIENT_ID = "placeholder-okta-id"
    env.NEXT_AUTH_OKTA_ISSUER = "https://placeholder.okta.com"
    env.NEXT_AUTH_OKTA_CLIENT_SECRET = "placeholder-okta-secret"
