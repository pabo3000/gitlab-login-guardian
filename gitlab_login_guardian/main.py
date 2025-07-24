from core import GitlabLoginGuardian

guardian = GitlabLoginGuardian(
    log_file="/var/log/gitlab/gitlab-rails/production_json.log",
    ban_log="/var/log/gitlab-login-ban.log",
    blocklist_file="/etc/gitlab/nginx/custom/ip_blocklist.conf",
    meta_file="/etc/gitlab/nginx/custom/ip_blocklist_meta.json",
)

guardian.monitor()
