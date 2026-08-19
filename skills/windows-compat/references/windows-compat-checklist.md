# Windows Compatibility Checklist

Use this checklist when code is written or modified on macOS but Windows is a supported target.

## Files and paths

- Build paths with platform-aware APIs instead of concatenating `/` or `\\` manually.
- Avoid hard-coded `/Users`, `/Applications`, `/Volumes`, drive letters, or user-specific absolute paths.
- Do not rely on filename case differences such as `Config.json` vs `config.json`.
- Avoid assuming Unix executable bits or symlink behavior unless the Windows path is verified.

## Processes and shell commands

- Prefer language process APIs with argument arrays.
- Avoid requiring `bash`, `zsh`, `open`, `osascript`, `pbcopy`, `pbpaste`, `launchctl`, or Homebrew.
- If a shell command is unavoidable, provide a Windows implementation and isolate the platform-specific selection.
- Quote/escape arguments through the process API instead of hand-building shell strings.

## Environment and configuration

- Use environment variables and application-data locations through platform-aware APIs.
- Do not assume `HOME` is the only home-directory variable.
- Treat separators in `PATH`-like variables as platform-dependent.
- Use UTF-8 explicitly where the runtime allows it; do not rely on a machine's legacy default encoding.

## GUI and native APIs

- AppKit and Cocoa are macOS-only.
- A native macOS UI is not a Windows UI implementation.
- Keep native integrations behind a small adapter so Windows can provide its own implementation.

## Networking and ports

- Avoid assuming a local hostname, interface name, or Unix-domain socket is available on Windows.
- When choosing ports, allow configuration and handle conflicts cleanly.

## Packaging

A successful Mac build does not imply a Windows package exists.

For Windows deliverables, verify the project's actual packaging path, for example the framework's supported Windows executable/installer workflow. Keep packaging configuration in source control when practical.

## Testing

At minimum:

1. run normal tests on the Mac development host;
2. run the compatibility scanner;
3. run Windows tests/builds in CI or on a Windows machine before claiming Windows verification.

If step 3 has not happened, report exactly that Windows runtime verification is still pending.
