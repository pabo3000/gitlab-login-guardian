#!/usr/bin/env python3

import time
from core import GitlabLoginGuardian

guardian = GitlabLoginGuardian(
    log_file="/var/log/gitlab/gitlab-rails/production_json.log",
    ban_log="/var/log/gitlab-login-ban.log",
    blocklist_file="/etc/gitlab/nginx/custom/ip_blocklist.conf",
    meta_file="/etc/gitlab/nginx/custom/ip_blocklist_meta.json",
)

guardian.log("GitLab Login Guardian started")

try:
    while True:
        guardian.process_fail2ban_log()
        guardian.cleanup()
        time.sleep(10)
except KeyboardInterrupt:
    guardian.log("GitLab Login Guardian stopped by user.")
