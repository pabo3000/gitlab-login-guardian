#!/bin/bash

set -e

echo "===> Updating gitlab-login-guardian..."

# Configuration
REPO_DIR="$(pwd)/gitlab-login-guardian"  # Use current directory as repo path

# Pull latest changes or clone repository if missing
if [ -d "$REPO_DIR/.git" ]; then
  echo "-> Pulling latest changes from GitHub..."
  git -C "$REPO_DIR" pull
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
