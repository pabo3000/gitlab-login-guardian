#!/bin/bash

set -e

echo "===> Updating gitlab-login-guardian..."

# Configuration
REPO_DIR="/opt/gitlab-login-guardian"
REPO_URL="https://github.com/pabo3000/gitlab-login-guardian.git"

# Pull latest changes or clone repository if missing
if [ -d "$REPO_DIR/.git" ]; then
  echo "-> Pulling latest changes from GitHub..."
  git -C "$REPO_DIR" pull
else
  echo "-> Cloning repository into \"$REPO_DIR\" ..."
  git clone "$REPO_URL" "$REPO_DIR"
fi

# Run setup script
echo "-> Running setup script..."
sudo "$REPO_DIR/setup.sh"

# Reload systemd and restart the service
echo "-> Reloading systemd and restarting service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart gitlab-ban-monitor.service

# Show service status
echo "-> Service status:"
sudo systemctl status gitlab-ban-monitor.service --no-pager

echo "✅ Update complete."
