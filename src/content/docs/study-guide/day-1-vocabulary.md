---
title: Day 1 Vocabulary
description: Glossary of terms and definitions from the Training 1 study guide.
---

Vocabulary — Study Guide Day 1

## Unix & Linux Background
- **Unix** — Original operating system developed at Bell Labs (1969); proprietary/closed-source, which motivated the creation of free alternatives.
- **GNU Project** — Richard Stallman's 1983 effort that built nearly a full free OS's worth of tools (editor, compiler, shell) but no kernel.
- **Linux kernel** — Linus Torvalds' 1991 kernel that filled GNU's missing piece, combining to form "GNU/Linux," a complete free OS.
- **Debian family** — Linux distro family using APT/`.deb` packages; includes Ubuntu, Zorin, Mint, Kali.
- **Enterprise Linux family** — Linux distro family using RPM/DNF/YUM packages; includes RHEL, Fedora, CentOS.
- **Arch family** — Linux distro family using Pacman; offers full user control at the cost of a steep learning curve.
- **Package manager** — Automates installing/updating/removing software and its dependencies (e.g. `apt`, `rpm`/`dnf`/`yum`, `pacman`).
- **snap** — Canonical's sandboxed, cross-distro, auto-updating alternative to `apt`; larger and slower but more secure by default.
- **AOSP (Android Open Source Project)** — The open-source base Android is built on; Google Android, Fire OS, LineageOS, GrapheneOS, and OEM variants all fork from it. Android runs the Linux kernel but is not a conventional GNU/Linux distro (different userspace: ART, Bionic, no GNU tools).
- **pyenv** — Tool for managing multiple Python versions on one machine; must be installed separately on Windows and WSL, since the builds aren't interchangeable.

## Filesystem
- **`ls`** — Lists directory contents.
- **`pwd`** — Prints the current working directory path.
- **`cd`** — Changes directory (`/` = root, `~` = home, `..` = parent, `.` = current).
- **`cat`** — Prints a file's contents.
- **`nano`** — Terminal-based text editor.
- **`echo`** — Prints text, or writes it to a file.
- **`whoami`** — Prints the current logged-in username.
- **`clear`** — Wipes the visible screen only; does not end the session.
- **`exit`** — Ends the current shell session.
- **`rm` / `rm -rf`** — Deletes files/directories; no undo, use carefully.
- **`/bin`** — Core program binaries.
- **`/home`** — User personal files.
- **`/usr`** — Installed software and libraries.
- **`/etc`** — System configuration files.
- **`/var`** — Files that change over time (logs, caches).
- **`/opt`** — Third-party software installs.
- **`/tmp`** — Temporary files.
- **`/boot`, `/sys`** — Low-level system files; should not be modified casually.

## Permissions
- **File ownership** — A separate concept from read/write/execute permission; the owner can always restore their own permissions even after `chmod 000`, and root bypasses permission checks entirely.
- **Numeric chmod** — Permission notation where read=4, write=2, execute=1, summed per digit for owner/group/other (e.g. `644` = owner read+write, group read, other read).
- **Symbolic chmod** — Permission notation using a target (`u`/`g`/`o`), an operator (`+`/`-`), and a permission letter (`r`/`w`/`x`), e.g. `chmod +x script.sh`.
- **`adduser` / `usermod -aG` / `groupadd`** — Commands for creating users, adding a user to a group (always with `-aG` together), and creating groups.
- **`sudo su`** — Switches into a persistent root session (exit with Ctrl+D); only users in the `sudo` group can use it, deliberately restricting who has unrestricted system power.

## grep / awk / sed
- **Regex** — A pattern-matching language applied across tools (`grep`, `sed`, `awk`, Python `re`, Bash `=~`); core syntax includes `.` (any char), `*`/`+`/`?` (repetition), `[abc]`/`[^abc]`/`[a-z]` (character classes), `^`/`$` (anchors), `{n}` (repetition count), `()` (groups), `|` (OR).
- **`grep`** — Searches text for pattern matches (`-E` extended regex, `-o` extract match only, `-i` case-insensitive).
- **`awk`** — Parses structured row/column data using a field delimiter (`-F,`) and positional fields (`$1`, `$2`, etc.), similar to SQL columns.
- **`sed`** — Performs search-and-replace on text; previews by default, `-i` modifies the file in place.
- **`re.search()`** — Python function that finds the first regex match in a string.
- **`re.findall()`** — Python function that finds all regex matches in a string.
- **`re.sub()`** — Python function that finds and replaces regex matches (e.g. for PII masking).
- **Named capture groups** — `(?P<name>...)` syntax that turns unstructured text into a structured dict via `.groupdict()`.

## Processes
- **`ps`** — Lists running processes.
- **`&`** — Suffix that runs a command in the background.
- **`nohup`** — Runs a command so it survives the terminal disconnecting ("no hangup").
- **`jobs`** — Lists background jobs for the current terminal session.
- **`kill <PID>`** — Terminates a process by its process ID.
- **`top` / `htop`** — Show live system resource usage (`q` to quit).
- **`free`** — Shows memory usage.
- **`df`** — Shows disk space usage.

## cron
- **cron** — Linux's built-in job scheduler, edited via `crontab -e`.
- **Cron syntax** — 5 fields, in order: minute, hour, day-of-month, month, weekday; `*` means "every" value for that field.
- **Commenting out a cron job** — Prefixing the line with `#` disables it without deleting it.
- **Apache Airflow** — A later-course orchestration tool that uses this exact same 5-field cron syntax to schedule jobs/DAGs.

## Shell Automation & Operational Logs
- **Shell script** — A text file containing a sequence of terminal commands, run top-to-bottom; starts with a shebang line (`#!/bin/bash`).
- **Shebang** — The `#!/bin/bash`-style first line of a script, telling the system which program should interpret it.
- **`chmod +x`** — Grants execute permission; required before `./script.sh` will run, since new files aren't executable by default.
- **`systemctl`** — Manages system services (`status`/`start`/`stop`/`restart`/`enable`/`disable`).
- **`journalctl`** — Views a service's logs (`q` to exit paginated output).
