# 🔐 GitLab Login Guardian

A Python script that monitors failed login attempts on a GitLab Omnibus instance and automatically bans abusive IPs at the NGINX level. It maintains an IP blocklist, reloads NGINX, and cleans up expired bans.

👉 [GitHub Repository](https://github.com/pabo3000/gitlab-login-guardian)

---

## 📋 Features

- Watches `/users/sign_in` events in `production_json.log`
- Tracks failed login attempts per IP address
- Bans IPs exceeding a retry limit by writing `deny` rules into NGINX
- Reloads NGINX automatically after each update
- Logs actions in a dedicated log file
- Automatically cleans up expired IP bans

---

## ⚙️ Configuration

The script uses the following internal constants:

```python
MAX_RETRIES = 3
FIND_TIME_SECONDS = 3600  # 1 hour
BAN_DURATION_HOURS = 164  # 1 week
```

## 🛠 Installation with setup.sh
To install GitLab Login Guardian easily, use the provided setup.sh script.

1. Clone the repository

```bash
git clone https://github.com/pabo3000/gitlab-login-guardian.git
cd gitlab-login-guardian
```
2. Run the setup script

```bash
chmod +x setup.sh
sudo ./setup.sh
```

This will:

Copy the monitoring script to /usr/local/bin/

Create and initialize required files in /etc/gitlab/nginx/custom/

Create a systemd service to monitor failed logins

Start and enable the service to run on boot

3. Configure GitLab NGINX
Add the following line to your /etc/gitlab/gitlab.rb:

```ruby
nginx['custom_gitlab_server_config'] = "include /etc/gitlab/nginx/custom/ip_blocklist.conf;"
```

Then apply the changes:

```bash
sudo gitlab-ctl reconfigure
```

That’s it — your GitLab server is now protected from repeated login attempts via dynamic NGINX IP banning. 💪

## 🔄 Update

To update GitLab Login Guardian to the latest version:

```bash
sudo /opt/gitlab-login-guardian/update.sh
```

This will:

Pull the latest changes from the GitHub repository

Restart the gitlab-ban-monitor.service systemd service

⚠️ Make sure you haven't made local changes in /opt/gitlab-login-guardian, or they might be overwritten.

## Uninstallation

To remove GitLab Login Guardian:

```bash
./uninstall.sh
```

## 📁 File Locations

### Purpose	Path
Log file	/var/log/gitlab-login-ban.log
IP blocklist	/etc/gitlab/nginx/custom/ip_blocklist.conf
IP metadata	/etc/gitlab/nginx/custom/ip_blocklist_meta.json

## ✅ Example ip_blocklist.conf

```nginx
deny 84.239.49.45;
deny 87.249.132.156;
deny 91.107.230.61;
deny 98.170.57.249;
deny 51.159.226.152;
allow all;
```

Important: All deny rules must appear before allow all; in the file.

## ✅ Observe the effort

Open 4 ssh terminals

1. Observe the attempts to sign in:
```tail -f /var/log/gitlab/gitlab-rails/production_json.log | jq -c 'select(.path == "/users/sign_in" and .method == "POST") | {time, remote_ip, user: (.params[]? | select(.key == "user") | .value.login)}'```

2. Observe the guardian's log: 
```tail -f /var/log/gitlab-login-ban.log```

3. Observe how nginx blocks: 
```tail -f /var/log/gitlab/nginx/gitlab_error.log```

4. Observe the banned ips and here you can unban: 
```nano /etc/gitlab/nginx/custom/ip_blocklist.conf```


## 📦 Ideas for Future Improvements

Optional: integrate with ufw or fail2ban

Optional: support whitelisting trusted IPs or networks

Optional: make parameters configurable via CLI or config file

Optional: email or webhook alert on new bans

## 🧾 License

MIT License — free for personal and commercial use.

## ✉️ Maintainer

🐙 https://github.com/pabo3000
