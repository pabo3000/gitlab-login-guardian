#!/usr/bin/env python3

import json
import time
import subprocess
import os
from collections import defaultdict
from datetime import datetime, timedelta

# === Configuration ===
LOGFILE = "/var/log/gitlab/gitlab-rails/production_json.log"
BAN_LOG = "/var/log/gitlab-login-ban.log"
MAX_RETRIES = 3
FIND_TIME_SECONDS = 3600  # 1 hour
NGINX_BLOCKLIST = "/etc/gitlab/nginx/custom/ip_blocklist.conf"
NGINX_META_FILE = "/etc/gitlab/nginx/custom/ip_blocklist_meta.json"
BAN_DURATION_HOURS = 164

# === State ===
SEEN = defaultdict(list)


# === Logging ===
def log(msg):
    timestamp = datetime.utcnow().isoformat()
    with open(BAN_LOG, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


# === Metadata handling ===
def load_block_meta():
    if not os.path.exists(NGINX_META_FILE) or os.path.getsize(NGINX_META_FILE) == 0:
        return {}
    with open(NGINX_META_FILE, "r") as f:
        return json.load(f)


def save_block_meta(meta):
    with open(NGINX_META_FILE, "w") as f:
        json.dump(meta, f, indent=2)


# === Cleanup expired bans ===
def cleanup_nginx_blocklist():
    meta = load_block_meta()
    now = datetime.utcnow()
    expired = [ip for ip, ts in meta.items() if now - datetime.fromisoformat(ts) > timedelta(hours=BAN_DURATION_HOURS)]

    if expired:
        if os.path.exists(NGINX_BLOCKLIST):
            with open(NGINX_BLOCKLIST, "r") as f:
                lines = f.readlines()
            with open(NGINX_BLOCKLIST, "w") as f:
                for line in lines:
                    if not any(f"deny {ip};" in line for ip in expired):
                        f.write(line)

        for ip in expired:
            del meta[ip]
            log(f"Removed expired IP {ip} from NGINX blocklist.")

        save_block_meta(meta)
        try:
            subprocess.run(["gitlab-ctl", "hup", "nginx"], check=True)
            log("Reloaded NGINX after cleanup.")
        except Exception as e:
            log(f"Failed to reload NGINX: {e}")


# === Add IP to nginx blocklist ===
def block_in_nginx(ip):
    meta = load_block_meta()
    if ip in meta:
        return  # already blocked

    try:
        with open(NGINX_BLOCKLIST, "a") as f:
            f.write(f"deny {ip};\n")
        meta[ip] = datetime.utcnow().isoformat()
        save_block_meta(meta)
        log(f"Blocked IP {ip} in NGINX.")
        subprocess.run(["gitlab-ctl", "hup", "nginx"], check=True)
        log("Reloaded NGINX after ban.")
    except Exception as e:
        log(f"Error blocking IP {ip} in NGINX: {e}")


# === Tail the GitLab log ===
def tail_log(filepath):
    with open(filepath, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line.strip()


# === Main Loop ===
def main():
    log("Started monitoring GitLab login attempts...")
    cleanup_nginx_blocklist()

    for line in tail_log(LOGFILE):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("path") != "/users/sign_in":
            continue

        ip = entry.get("remote_ip")
        if not ip:
            continue

        now = datetime.utcnow()
        SEEN[ip] = [t for t in SEEN[ip] if now - t < timedelta(seconds=FIND_TIME_SECONDS)]
        SEEN[ip].append(now)

        log(f"Login attempt from IP {ip}, attempts: {len(SEEN[ip])}")

        if len(SEEN[ip]) >= MAX_RETRIES:
            log(f"Banning IP {ip} due to repeated login attempts.")
            block_in_nginx(ip)


if __name__ == "__main__":
    main()
