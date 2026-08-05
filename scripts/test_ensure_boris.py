#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENSURE_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "ensure-boris.sh")
CLEAN_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "clean-binaries.sh")
VERSION_CONFIG = os.path.join(PROJECT_ROOT, "metadata", "boris-version.json")

with open(VERSION_CONFIG, "r") as f:
    VERSION_DATA = json.load(f)
PINNED_COMMIT = VERSION_DATA["commit"]

def make_executable(path, content="#!/bin/sh\nexit 0\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o755)

def file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

class TestEnsureBoris(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test_boris_")
        self.repo_root = os.path.join(self.tmpdir, "thermalextractiondevices.com")
        os.makedirs(os.path.join(self.repo_root, "bin"), exist_ok=True)
        os.makedirs(os.path.join(self.repo_root, "metadata"), exist_ok=True)
        os.makedirs(os.path.join(self.repo_root, "scripts"), exist_ok=True)

        shutil.copy(ENSURE_SCRIPT, os.path.join(self.repo_root, "scripts", "ensure-boris.sh"))
        shutil.copy(CLEAN_SCRIPT, os.path.join(self.repo_root, "scripts", "clean-binaries.sh"))
        shutil.copy(VERSION_CONFIG, os.path.join(self.repo_root, "metadata", "boris-version.json"))

        os.chmod(os.path.join(self.repo_root, "scripts", "ensure-boris.sh"), 0o755)
        os.chmod(os.path.join(self.repo_root, "scripts", "clean-binaries.sh"), 0o755)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_script(self, script_path, args=None, env_override=None, cwd=None):
        env = os.environ.copy()
        for var in ["BORIS_BIN", "BORIS_AUTO_PROVISION", "BORIS_COMMIT", "BORIS_COMMIT_OVERRIDE"]:
            env.pop(var, None)
        if env_override:
            env.update(env_override)
        cmd = [script_path] + (args or [])
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd or self.repo_root,
            env=env
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

    def test_explicit_boris_bin_override(self):
        custom_bin = os.path.join(self.tmpdir, "custom_boris")
        make_executable(custom_bin)

        rc, stdout, stderr = self.run_script(
            os.path.join(self.repo_root, "scripts", "ensure-boris.sh"),
            env_override={"BORIS_BIN": custom_bin}
        )
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, custom_bin)

    def test_valid_manifest_short_circuits(self):
        target_bin = os.path.join(self.repo_root, "bin", "boris")
        manifest_file = os.path.join(self.repo_root, "bin", "boris.json")
        make_executable(target_bin, "#!/bin/sh\necho boris\n")

        binary_sha = file_sha256(target_bin)
        manifest_data = {
            "binary": target_bin,
            "source": "test",
            "repository": VERSION_DATA["repository"],
            "branch": VERSION_DATA["branch"],
            "commit": PINNED_COMMIT,
            "zig_version": VERSION_DATA["zig_version"],
            "checksum": binary_sha,
            "built_at": "2026-01-01T00:00:00Z"
        }
        with open(manifest_file, "w") as f:
            json.dump(manifest_data, f)

        rc, stdout, stderr = self.run_script(
            os.path.join(self.repo_root, "scripts", "ensure-boris.sh")
        )
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, target_bin)

if __name__ == "__main__":
    unittest.main()
