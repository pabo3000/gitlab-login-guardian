#!/bin/bash
set -e

echo "🔐 Setting up GitLab Login Guardian..."

# Configuration
SCRIPT_SOURCE="ban_gitlab_logins.py"
SCRIPT_DEST="/usr/local/bin/ban_gitlab_logins.py"
BLOCKLIST_DIR="/etc/gitlab/nginx/custom"
BLOCKLIST_FILE="$BLOCKLIST_DIR/ip_blocklist.conf"
META_FILE="$BLOCKLIST_DIR/ip_blocklist_meta.json"
LOGFILE="/var/log/gitlab-login-ban.log"
SERVICE_FILE="/etc/systemd/system/gitlab-ban-monitor.service"

# 1. Ensure necessary directories exist
echo "📁 Creating required directories..."
sudo mkdir -p "$BLOCKLIST_DIR"

# 2. Copy the script and create log/meta files
echo "📄 Copying script and creating metadata files..."
sudo cp "$SCRIPT_SOURCE" "$SCRIPT_DEST"
sudo chmod +x "$SCRIPT_DEST"

sudo touch "$BLOCKLIST_FILE"
sudo touch "$META_FILE"
sudo chmod 644 "$BLOCKLIST_FILE" "$META_FILE"

sudo touch "$LOGFILE"
sudo chmod 644 "$LOGFILE"

# 3. Create the systemd service unit
echo "⚙️ Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Monitor GitLab failed login attempts and ban IPs via NGINX
After=network.target

[Service]
ExecStart=$SCRIPT_DEST
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# 4. Enable and start the service
echo "🚀 Enabling and starting the service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now gitlab-ban-monitor.service

# 5. Reminder for gitlab.rb configuration
echo
echo "📌 Please make sure the following line is present in your /etc/gitlab/gitlab.rb:"
echo
echo "nginx['custom_gitlab_server_config'] = \"include $BLOCKLIST_FILE;\""
echo
echo "Then apply the config with: sudo gitlab-ctl reconfigure"

echo "✅ GitLab Login Guardian setup complete."