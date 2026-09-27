#!/usr/bin/env python3
"""The Sunday Smoke web server (Tailscale-only; mounted at /sunday-smoke/ under the Newsstand). Static pages.
Usage: serve.py <site_dir> <host> <port>"""
import os, sys
import gardenweb as gw


class Handler(gw.Handler):
    ROOT = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    gw.run(Handler, sys.argv[1], sys.argv[2], int(sys.argv[3]))
