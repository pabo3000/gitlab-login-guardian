#!/bin/bash
# uninstall.sh - Remove GitLab Login Guardian service and related files

set -e

echo "Stopping systemd service..."
sudo systemctl stop gitlab-login-guardian.service || true
sudo systemctl disable gitlab-login-guardian.service || true

echo "Removing systemd service unit..."
sudo rm -f /etc/systemd/system/gitlab-login-guardian.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "Removing installed files..."
sudo rm -f /usr/local/bin/ban_gitlab_logins.py
sudo rm -f /var/log/gitlab-login-ban.log
sudo rm -f /etc/gitlab/nginx/custom/ip_blocklist.conf
sudo rm -f /etc/gitlab/nginx/custom/ip_blocklist_meta.json

echo "Optionally remove the whole nginx custom config directory (y/n)?"
read -r answer
if [[ "$answer" == "y" ]]; then
  sudo rm -rf /etc/gitlab/nginx/custom
fi

echo "Uninstall complete."
