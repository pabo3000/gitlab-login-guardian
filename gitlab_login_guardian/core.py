import json
import time
import subprocess
import os
from collections import defaultdict
from datetime import datetime, timedelta

MAX_RETRIES = 3
FIND_TIME_SECONDS = 3600  # 1 hour
BAN_DURATION_HOURS = 164  # 1 week


class GitlabLoginGuardian:
    def __init__(self, log_file, ban_log, blocklist_file, meta_file):
        self.log_file = log_file
        self.ban_log = ban_log
        self.blocklist_file = blocklist_file
        self.meta_file = meta_file

        self.banned = set()
        self.seen = defaultdict(list)

    def log(self, msg):
        timestamp = datetime.utcnow().isoformat()
        with open(self.ban_log, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")

    def load_meta(self):
        if not os.path.exists(self.meta_file) or os.path.getsize(self.meta_file) == 0:
            return {}
        with open(self.meta_file, "r") as f:
            return json.load(f)

    def save_meta(self, meta):
        with open(self.meta_file, "w") as f:
            json.dump(meta, f, indent=2)

    def cleanup(self):
        meta = self.load_meta()
        now = datetime.utcnow()
        expired = [ip for ip, ts in meta.items() if now - datetime.fromisoformat(ts) > timedelta(hours=BAN_DURATION_HOURS)]

        if expired:
            if os.path.exists(self.blocklist_file):
                with open(self.blocklist_file, "r") as f:
                    lines = f.readlines()
                with open(self.blocklist_file, "w") as f:
                    for line in lines:
                        if not any(f"deny {ip};" in line for ip in expired):
                            f.write(line)

            for ip in expired:
                del meta[ip]
                self.log(f"Removed expired IP {ip} from NGINX blocklist.")

            self.save_meta(meta)
            try:
                subprocess.run(["gitlab-ctl", "hup", "nginx"], check=True)
                self.log("Reloaded NGINX after cleanup.")
            except Exception as e:
                self.log(f"Failed to reload NGINX: {e}")

    def block_ip(self, ip):
        meta = self.load_meta()
        if ip in meta:
            return  # already blocked

        meta[ip] = datetime.utcnow().isoformat()
        self.save_meta(meta)
        
        allow_seen = False
        lines = []

        # Load current blocklist if exists
        if os.path.exists(self.blocklist_file):
            with open(self.blocklist_file, "r") as f:
                for line in f:
                    if "allow all;" in line:
                        allow_seen = True
                        break
                    if line.strip() and not line.strip().startswith("#"):
                        lines.append(line.strip())

        # Extract deny IPs
        deny_ips = set()
        for line in lines:
            if line.startswith("deny"):
                deny_ip = line.replace("deny", "").replace(";", "").strip()
                deny_ips.add(deny_ip)

        # Add new IP to deny list
        deny_ips.add(ip)

        # Sort and reconstruct blocklist
        sorted_lines = [f"deny {deny};" for deny in sorted(deny_ips)]
        sorted_lines.append("allow all;")

        # Write to blocklist
        try:
            with open(self.blocklist_file, "w") as f:
                for line in sorted_lines:
                    f.write(f"{line}\n")

            self.log(f"IP {ip} added to NGINX blocklist.")
            subprocess.run(["gitlab-ctl", "hup", "nginx"], check=True)
            self.log("Reloaded NGINX after blocking IP.")
        except Exception as e:
            self.log(f"Error blocking {ip} in NGINX: {e}")

    def tail_log(self):
        with open(self.log_file, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                yield line.strip()

    def monitor_logins(self):
        self.log("Starting GitLab login monitoring...")
        self.cleanup()

        for line in self.tail_log():
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
            self.seen[ip] = [t for t in self.seen[ip] if now - t < timedelta(seconds=FIND_TIME_SECONDS)]
            self.seen[ip].append(now)

            self.log(f"Login attempt from IP {ip}, attempts: {len(self.seen[ip])}")

            if len(self.seen[ip]) >= MAX_RETRIES:
                self.log(f"Blocking IP {ip} due to repeated login attempts.")
                self.block_ip(ip)
