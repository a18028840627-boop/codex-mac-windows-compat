# AGENTS.md

## Mission

This repository exists to prevent macOS-hosted Codex work from accidentally becoming macOS-only when the intended target is Windows or cross-platform.

## Default rule

If the user says the program must run on Windows, treat **Windows compatibility as a release requirement**, even when development and testing are happening on macOS.

The current host OS is evidence about the development environment, not permission to change the target platform.

## Implementation rules

1. Prefer cross-platform standard-library or framework APIs over OS-specific shell commands.
2. Never hard-code macOS paths such as `/Users/...`, `/Applications/...`, or `/Volumes/...` into application logic.
3. Build filesystem paths with platform-aware APIs such as `pathlib`, `os.path`, `Path`, or the language/framework equivalent.
4. Do not assume `/bin/bash`, `zsh`, `open`, `osascript`, `pbcopy`, `launchctl`, Homebrew, AppKit, Cocoa, or other macOS-only facilities exist on Windows.
5. When OS-specific behavior is genuinely required, isolate it behind an explicit platform abstraction and provide a Windows implementation or a clear unsupported-platform error.
6. Prefer process APIs with argument arrays over shell-concatenated command strings.
7. Do not rely on case-sensitive filenames, executable permission bits, Unix symlinks, or LF-only behavior unless the target stack explicitly supports them.
8. Treat text encoding, path separators, environment variables, process launching, file locking, and line endings as cross-platform concerns.
9. For packaging, produce or document a Windows-compatible build path. A `.app`, DMG, Homebrew formula, or macOS-only bundle is not a Windows deliverable.
10. Never claim "Windows verified" based only on a successful macOS run.

## Verification rules

Before considering a Windows-targeted change complete:

- Run relevant unit/integration tests on the current host.
- Run `skills/windows-compat/scripts/compat_scan.py` against the changed project when available.
- If a Windows runner or Windows machine is available, run the Windows test/build path there.
- If Windows execution was not performed, say explicitly: `Windows runtime verification pending`.

## Change discipline

Keep portability fixes small and local. Do not rewrite architecture just to achieve compatibility unless the existing architecture makes Windows support impossible.
