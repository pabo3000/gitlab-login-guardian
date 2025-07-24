#!/bin/bash
set -e

echo "🔐 Setting up GitLab Login Guardian..."

# === Configuration ===
REPO_DIR="$(pwd)/gitlab-login-guardian"
SCRIPT_SOURCE="gitlab_login_guardian/main.py"
SCRIPT_DEST="/usr/local/bin/gitlab_login_guardian"
BLOCKLIST_DIR="/etc/gitlab/nginx/custom"
BLOCKLIST_FILE="$BLOCKLIST_DIR/ip_blocklist.conf"
META_FILE="$BLOCKLIST_DIR/ip_blocklist_meta.json"
LOGFILE="/var/log/gitlab-login-ban.log"
SERVICE_FILE="/etc/systemd/system/gitlab-ban-monitor.service"

# === 1. Prepare directories ===
echo "📁 Creating required directories..."
sudo mkdir -p "$BLOCKLIST_DIR"
sudo mkdir -p "$(dirname "$SCRIPT_DEST")"
sudo mkdir -p "$(dirname "$LOGFILE")"

# === 2. Copy main script to /usr/local/bin ===
echo "📄 Installing main script..."
sudo cp "$SCRIPT_SOURCE" "$SCRIPT_DEST/main.py"
sudo chmod +x "$SCRIPT_DEST"

# === 3. Create empty log and metadata files ===
echo "🛠️ Creating metadata and log files..."
sudo touch "$BLOCKLIST_FILE" "$META_FILE" "$LOGFILE"
sudo chmod 644 "$BLOCKLIST_FILE" "$META_FILE" "$LOGFILE"

# === 4. Create systemd service ===
echo "⚙️ Creating systemd service unit..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Monitor GitLab failed login attempts and ban IPs via NGINX
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_DEST/main.py

Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# === 5. Enable and start service ===
echo "🚀 Enabling and starting the service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now gitlab-ban-monitor.service

# === 6. Reminder for gitlab.rb ===
echo
echo "📌 Please make sure this line is present in /etc/gitlab/gitlab.rb:"
echo
echo "nginx['custom_gitlab_server_config'] = \"include $BLOCKLIST_FILE;\""
echo
echo "Then apply the config with: sudo gitlab-ctl reconfigure"

echo "✅ GitLab Login Guardian setup complete."
