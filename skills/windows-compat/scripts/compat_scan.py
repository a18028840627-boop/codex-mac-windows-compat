#!/usr/bin/env python3
"""Scan source trees for common macOS-only assumptions.

This is intentionally conservative: findings are review prompts, not proof that code
is incompatible. The script uses only the Python standard library and runs on macOS,
Windows, and Linux.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    "coverage",
    "__pycache__",
}

TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".java", ".kt", ".kts", ".go", ".rs", ".rb", ".php",
    ".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".swift",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".xml", ".gradle", ".properties",
}

TEXT_NAMES = {
    "Dockerfile",
    "Makefile",
    "CMakeLists.txt",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    pattern: re.Pattern[str]
    message: str


RULES = [
    Rule("MAC_PATH_USERS", "error", re.compile(r"(?<![A-Za-z0-9_])/Users/[^\s\"']+"), "Hard-coded macOS /Users path."),
    Rule("MAC_PATH_APPS", "error", re.compile(r"(?<![A-Za-z0-9_])/Applications/[^\s\"']+"), "Hard-coded macOS /Applications path."),
    Rule("MAC_PATH_VOLUMES", "error", re.compile(r"(?<![A-Za-z0-9_])/Volumes/[^\s\"']+"), "Hard-coded macOS /Volumes path."),
    Rule("OSASCRIPT", "error", re.compile(r"\bosascript\b"), "osascript is macOS-only."),
    Rule("PBCOPY", "error", re.compile(r"\b(?:pbcopy|pbpaste)\b"), "pbcopy/pbpaste are macOS-only."),
    Rule("LAUNCHCTL", "error", re.compile(r"\blaunchctl\b"), "launchctl is macOS-only."),
    Rule("OPEN_APP", "warning", re.compile(r"\bopen\s+(?:-a\s+)?"), "The macOS 'open' command needs a Windows alternative or platform guard."),
    Rule("DEFAULTS_CMD", "warning", re.compile(r"\bdefaults\s+(?:read|write|delete)\b"), "The macOS defaults command needs a Windows alternative or platform guard."),
    Rule("APPKIT_IMPORT", "error", re.compile(r"(?:^|\s)(?:import|from)\s+(?:AppKit|Cocoa)\b", re.MULTILINE), "AppKit/Cocoa is macOS-only."),
    Rule("SHELL_BIN", "warning", re.compile(r"/(?:bin|usr/bin)/(?:bash|zsh)\b"), "Absolute Unix shell path will not exist on normal Windows installs."),
    Rule("DARWIN_BRANCH", "info", re.compile(r"(?:sys\.platform\s*==\s*[\"']darwin[\"']|platform\.system\(\)\s*==\s*[\"']Darwin[\"'])"), "macOS-specific branch found; confirm an equivalent Windows path exists."),
]


@dataclass
class Finding:
    severity: str
    rule_id: str
    path: str
    line: int
    message: str
    excerpt: str


def is_text_candidate(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def iter_files(root: Path):
    if root.is_file():
        if is_text_candidate(root):
            yield root
        return

    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.is_file() and is_text_candidate(path):
            yield path


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_file(path: Path, display_root: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    findings: list[Finding] = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            line = line_number(text, match.start())
            source_line = text.splitlines()[line - 1].strip() if text.splitlines() else ""
            try:
                shown_path = str(path.relative_to(display_root))
            except ValueError:
                shown_path = str(path)
            findings.append(
                Finding(
                    severity=rule.severity,
                    rule_id=rule.rule_id,
                    path=shown_path,
                    line=line,
                    message=rule.message,
                    excerpt=source_line[:180],
                )
            )
    return findings


def scan(root: Path) -> list[Finding]:
    root = root.resolve()
    display_root = root if root.is_dir() else root.parent
    findings: list[Finding] = []
    for path in iter_files(root):
        # Do not scan this scanner's own rule literals when scanning the skill repo.
        if path.resolve() == Path(__file__).resolve():
            continue
        findings.extend(scan_file(path, display_root))
    return sorted(findings, key=lambda f: (f.path, f.line, f.rule_id))


def print_human(findings: list[Finding]) -> None:
    if not findings:
        print("No common macOS-only assumptions found.")
        return
    for item in findings:
        print(f"[{item.severity.upper()}] {item.path}:{item.line} {item.rule_id} - {item.message}")
        if item.excerpt:
            print(f"  {item.excerpt}")
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    infos = sum(item.severity == "info" for item in findings)
    print(f"\nSummary: {errors} error(s), {warnings} warning(s), {infos} info finding(s).")


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "safe.py").write_text("from pathlib import Path\nprint(Path.home())\n", encoding="utf-8")
        (root / "bad.py").write_text('import subprocess\nsubprocess.run(["osascript", "-e", "display dialog test"])\n', encoding="utf-8")
        findings = scan(root)
        if not any(f.rule_id == "OSASCRIPT" and f.path == "bad.py" for f in findings):
            print("Self-test failed: expected OSASCRIPT finding.", file=sys.stderr)
            return 1
        if any(f.path == "safe.py" and f.severity == "error" for f in findings):
            print("Self-test failed: safe file produced an error finding.", file=sys.stderr)
            return 1
    print("Self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for common macOS-only assumptions in Windows-targeted projects.")
    parser.add_argument("path", nargs="?", default=".", help="File or directory to scan (default: current directory).")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON instead of human-readable output.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in cross-platform self-test.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    findings = scan(root)
    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    else:
        print_human(findings)

    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
