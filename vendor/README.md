# Bundled Codex

Run `./codex` from the repository root. No Codex installer is needed.

The complete Linux x86_64 release package lives in `codex/linux-x86_64/`,
including its runtime resources and bundled third-party notices.
Other operating systems and CPU architectures need a different build.

Executables and shared libraries are stored through Git LFS. Clone with Git
LFS available; if the launcher reports pointer files, run `git lfs pull`.

Sign in with `./codex login --device-auth`. Each reader uses their own account.
Credentials, sessions, caches, and temporary files stay in `.codex-home/`,
which Git ignores. Exclude that directory when sharing a ZIP or folder copy.
