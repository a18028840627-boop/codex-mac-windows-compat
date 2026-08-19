# Codex Mac → Windows Compatibility

A small compatibility toolkit for a common workflow: **develop with Codex on macOS, but make sure the result still works on Windows**.

## Goal

The host machine is not the target platform. When a project is intended for Windows, Codex should not quietly introduce macOS-only paths, commands, APIs, packaging assumptions, or verification claims.

## What this repository provides

- `AGENTS.md` — repository-level compatibility rules for Codex.
- `skills/windows-compat/SKILL.md` — a reusable Codex skill for Mac → Windows development.
- `skills/windows-compat/scripts/compat_scan.py` — a standard-library-only scanner for common macOS-only assumptions.
- `skills/windows-compat/references/windows-compat-checklist.md` — practical review checklist.
- `tests/test_compat_scan.py` — standard-library regression tests for the scanner.
- `.github/workflows/compat-self-test.yml` — runs the scanner tests on both macOS and Windows.

## Recommended use

### 1. Install the reusable skill

Use Codex's built-in skill installer to install the `skills/windows-compat` folder from this repository, or copy that folder into your Codex skills directory (`$CODEX_HOME/skills`, normally `~/.codex/skills`).

### 2. Use it in a project

When starting work that must run on Windows, invoke:

```text
$windows-compat
```

The skill tells Codex to treat Windows compatibility as a release requirement even when the current development host is a Mac.

### 3. Run the compatibility scan

```bash
python skills/windows-compat/scripts/compat_scan.py <project-path>
```

The scanner reports common macOS-only assumptions such as hard-coded `/Users/...` paths, `osascript`, `pbcopy`, `launchctl`, AppKit/Cocoa imports, and similar patterns.

### 4. Run the regression tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Important limitation

A clean scan is **not** proof that a program works on Windows. It is an early warning layer. Real Windows verification should still run on Windows or a Windows CI runner before release.

## Status

V0.2 scanner hardening.
