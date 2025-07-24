import os
import json
import shutil
from datetime import datetime, timedelta
from gitlab_login_guardian import GitlabLoginGuardian

TEST_IP = "203.0.113.42"


def test_block_and_cleanup_with_fixtures(tmp_path):
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")

    # Copy fixture files into the temporary test directory
    shutil.copy(os.path.join(fixture_dir, "ip_blocklist_meta.json"), tmp_path / "ip_blocklist_meta.json")
    shutil.copy(os.path.join(fixture_dir, "ip_blocklist.conf"), tmp_path / "ip_.conf")
    shutil.copy(os.path.join(fixture_dir, "ban.log"), tmp_path / "ban.log")

    meta_path = tmp_path / "meta.json"
    blocklist_path = tmp_path / "blocklist.conf"
    ban_log_path = tmp_path / "ban.log"

    guardian = GitlabLoginGuardian(
        log_file="/dev/null",
        ban_log=str(ban_log_path),
        blocklist_file=str(blocklist_path),
        meta_file=str(meta_path),
    )

    # Test blocking
    guardian.block_ip(TEST_IP)

    # Assert IP is in blocklist
    with open(blocklist_path) as f:
        assert f"deny {TEST_IP};" in f.read()

    # Assert IP is in meta
    with open(meta_path) as f:
        meta = json.load(f)
    assert TEST_IP in meta

    # Simulate expiration and test cleanup
    meta[TEST_IP] = (datetime.utcnow() - timedelta(hours=200)).isoformat()
    guardian.save_meta(meta)

    guardian.cleanup()

    with open(meta_path) as f:
        cleaned_meta = json.load(f)
    assert TEST_IP not in cleaned_meta

    with open(blocklist_path) as f:
        assert f"deny {TEST_IP};" not in f.read()
