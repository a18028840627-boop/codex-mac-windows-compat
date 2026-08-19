from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "skills" / "windows-compat" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import compat_scan


class CompatScanTests(unittest.TestCase):
    def test_detects_representative_macos_assumptions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_dir = root / "src"
            source_dir.mkdir()
            (source_dir / "unsafe.py").write_text(
                'USER = "/Users/example/app"\n'
                'import AppKit\n'
                'subprocess.run(["osascript"])\n'
                'subprocess.run(["/bin/bash", "-lc", "echo ok"])\n'
                'platform.system() == "Darwin"\n',
                encoding="utf-8",
            )

            findings = compat_scan.scan(root)
            rule_ids = {finding.rule_id for finding in findings}

            self.assertTrue(
                {
                    "MAC_PATH_USERS",
                    "OSASCRIPT",
                    "APPKIT_IMPORT",
                    "SHELL_BIN",
                    "DARWIN_BRANCH",
                }.issubset(rule_ids)
            )
            self.assertEqual(
                {str(Path("src") / "unsafe.py")},
                {finding.path for finding in findings},
            )

    def test_scans_project_when_parent_directory_is_named_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "build"
            root.mkdir()
            (root / "unsafe.py").write_text(
                'subprocess.run(["osascript"])\n',
                encoding="utf-8",
            )

            findings = compat_scan.scan(root)

            self.assertIn("OSASCRIPT", {finding.rule_id for finding in findings})

    def test_skips_nested_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "build"
            generated.mkdir()
            (generated / "unsafe.py").write_text(
                'subprocess.run(["osascript"])\n',
                encoding="utf-8",
            )

            self.assertEqual([], compat_scan.scan(root))


if __name__ == "__main__":
    unittest.main()
