---
name: windows-compat
description: Use when developing, reviewing, packaging, or fixing software on macOS that must also run on Windows. Prevent macOS-only paths, commands, APIs, dependencies, packaging assumptions, and false Windows-verification claims.
---

# Windows Compatibility

Use this skill whenever the current development machine is macOS but the intended target includes Windows.

## Core principle

**Host OS is not target OS.**

Do not choose a macOS-only implementation just because it is convenient on the current machine.

## Workflow

### 1. Establish the target

Treat Windows as required when the user says any equivalent of:

- "must work on Windows"
- "Mac development, Windows deployment"
- "cross-platform"
- "package as a Windows app/exe"

If the project already declares Windows support, preserve it unless the user explicitly changes the target.

### 2. Inspect before changing

Check the relevant project files for:

- hard-coded POSIX/macOS paths
- shell commands and subprocess calls
- platform-specific imports
- native GUI/system frameworks
- packaging/build configuration
- file/path handling
- environment-variable assumptions
- line-ending or permission assumptions

When available, run:

```bash
python scripts/compat_scan.py <project-path>
```

Resolve the script path relative to this skill directory.

### 3. Implement portably

Prefer:

- path APIs instead of string-built paths
- standard process APIs instead of shell-specific commands
- explicit platform adapters when behavior truly differs
- cross-platform libraries already used by the project
- runtime data/config directories supplied by the framework or OS

Do not silently add dependencies on macOS-only facilities such as `osascript`, `open`, `pbcopy`, `launchctl`, AppKit, Cocoa, or hard-coded `/Users/...` paths.

### 4. Keep platform-specific code isolated

When one implementation cannot serve both platforms:

1. define a small common interface;
2. put macOS behavior in a macOS-specific adapter;
3. put Windows behavior in a Windows-specific adapter;
4. select the adapter explicitly from the platform;
5. keep business logic platform-neutral.

Do not scatter platform checks throughout unrelated code.

### 5. Verify honestly

Run the project's normal tests on the current machine.

If Windows CI or a Windows machine is available, run the Windows build/test path too.

If it is not available, do **not** claim Windows is verified. Report:

`Windows runtime verification pending.`

A clean static scan means only that common compatibility hazards were not found.

## Release checklist

Before declaring the work ready:

- no hard-coded macOS user/application/volume paths in runtime code
- no unguarded macOS-only commands or native frameworks
- paths are built with platform-aware APIs
- process launching does not depend on a Unix shell unless explicitly required
- Windows packaging/build instructions exist when a distributable is requested
- Windows tests/builds were run, or the lack of Windows runtime verification is stated clearly

For detailed review guidance, read `references/windows-compat-checklist.md`.
