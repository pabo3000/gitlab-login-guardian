# GitLab Login Guardian

A monitoring script that automatically blocks IP addresses in NGINX (GitLab Omnibus) after repeated failed login attempts.

## Features
- Monitors GitLab's production JSON log
- Blocks IPs via NGINX include file
- Cleans up expired blocks
- Requires no modification of GitLab internals

## Installation
See `setup.py` or use `pip install .` in this folder.
