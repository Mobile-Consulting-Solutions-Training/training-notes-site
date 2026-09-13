---
title: Study Guide - Day 1
description: Quick summary, cheat sheet, and flashcards for Training 1 (Linux and Shell Scripting)
---

Study Guide - Day 1 (source: notes/Training 1.md)

# Part 1: Quick Summary

**Unix & Linux Background.** Unix originated at Bell Labs (1969) but was proprietary - this gap motivated Richard Stallman's GNU Project (1983), which built almost everything needed for a free OS (editor, compiler, shell) except a kernel. Linus Torvalds' Linux kernel (1991) filled that gap - combined, "GNU/Linux" became a complete free OS. Being free AND open source made it the default choice for data centers over paying for proprietary Unix/Windows licensing at scale - this is why Linux underlies most servers and Big Data tooling today. Linux isn't one OS but a family of distributions, grouped into three major families: Debian (APT/`.deb` - Ubuntu, Zorin, Mint), Enterprise Linux (RPM - Red Hat, Fedora, CentOS), and Arch (Pacman - full user control, steep learning curve). A package manager automates downloading/installing software; `snap` is Canonical's newer sandboxed universal alternative to `apt`. Android runs the Linux kernel but is not a conventional GNU/Linux distro - it shares the kernel but builds a totally different userspace (ART, Bionic, no GNU tools); AOSP is the open base, with Google's proprietary layer, Fire OS, LineageOS, and GrapheneOS all forking from it. `pyenv` manages multiple Python versions per-machine (install separately for Windows and WSL); avoid Anaconda's bloat in favor of a lightweight pyenv-managed install.

**Filesystem.** Core navigation/inspection commands: `ls` (list), `pwd` (show current path), `cd` (change directory - `/` for root, `~` for home, `..` for parent, `.` for current), `cat` (print file contents), `nano` (edit files), `echo` (print text/write to files), `whoami` (current user), `clear` (wipe screen, doesn't end session) vs `exit` (ends session), and `rm`/`rm -rf` (delete - no undo, be careful). The root filesystem has standard top-level directories: `/bin` (core program binaries), `/home` (user files), `/usr` (installed software/libraries), `/etc` (system config), `/var` (logs/caches), `/opt` (third-party installs), `/tmp` (temp files), `/boot` and `/sys` (don't touch).

**Permissions.** File ownership and read/write/execute permission are separate concepts - even with `chmod 000`, the owner can still change permissions back (root can always bypass permission checks too). Numeric chmod uses read=4/write=2/execute=1 summed per owner/group/other digit (e.g. `644` = owner rw, group r, other r). Symbolic chmod uses `u`/`g`/`o` + `+`/`-` + `r`/`w`/`x` (e.g. `chmod +x script.sh` to make a script runnable - required before `./script.sh` will work, since new files aren't executable by default). User/group management: `adduser`, `usermod -aG <group> <user>`, `groupadd`, `groups <user>`. `sudo` access is restricted to the `sudo` group deliberately, to limit blast radius from mistakes or bad actors.

**grep / awk / sed.** Regex is one pattern language applied differently across tools (`grep`, `sed`, `awk`, Python's `re`, Bash's `=~`). Core syntax: `.` any char, `*`/`+`/`?` repetition, `[abc]`/`[^abc]`/`[a-z]` character classes, `^`/`$` anchors, `{n}` repetition count, `()` groups, `|` OR. `grep` searches text (`-E` for extended regex, `-o` to extract just the match, `-i` case-insensitive); `awk -F,` parses column/row structured data (`$1`, `$2`, etc., like SQL columns); `sed 's/old/new/'` previews a replace, `sed -i` actually modifies the file. Python's `re` module: `re.search()` finds one match, `re.findall()` finds all, `re.sub()` replaces (useful for PII masking), named groups (`(?P<name>...)`) turn unstructured text into structured dicts.

**Processes.** `ps` / `ps aux | grep <name>` shows running processes; `&` backgrounds a command; `nohup` keeps it running after the terminal disconnects; `jobs` lists background jobs (per-terminal); `kill <PID>` stops a process. `top`/`htop` show live resource usage; `free` shows memory; `df` shows disk space.

**cron.** Built-in Linux scheduler, edited via `crontab -e`. Syntax is 5 fields: minute, hour, day-of-month, month, weekday, with `*` meaning "every". E.g. `30 9 * * 1` = every Monday at 9:30am. Comment out a line with `#` to disable without deleting. Apache Airflow (covered later in the course) uses this exact same cron syntax to schedule jobs/DAGs.

**Shell Automation & Operational Logs.** A shell script is just a list of terminal commands in a file, run top-to-bottom, starting with a shebang line (`#!/bin/bash`) and needing `chmod +x` before `./script.sh` will run. Useful for provisioning a new server end-to-end in one execution. `systemctl status/start/stop/restart/enable/disable <service>` manages system services; `journalctl <service>` views their logs (press `q` to exit paginated output).

---

# Part 2: Cheat Sheet

## Unix & Linux Background
- **Unix** (Bell Labs, 1969): proprietary -> **GNU** (Stallman, 1983): free tools, no kernel -> **Linux kernel** (Torvalds, 1991): the missing piece -> **GNU/Linux**: complete free OS.
- Free + open source = won data centers over paying per-machine for Unix/Windows licenses. WSL's existence = Microsoft conceding the server OS war to Linux.
- **3 distro families**: Debian (`.deb`/APT - Ubuntu, Zorin, Mint, Kali) | Enterprise Linux (`.rpm`/RPM,DNF,YUM - RHEL, Fedora, CentOS) | Arch (Pacman - full control, steep curve).
- Ubuntu = most flexible major distro, good for beginners. Zorin = Windows-like, beginner-friendly. CentOS was deprecated by Red Hat after acquisition.
- **Package manager**: automates install/update/remove of software + dependencies. `apt`/`apt-get` (Debian), `rpm`/`dnf`/`yum` (Enterprise), `pacman` (Arch). `snap` = Canonical's sandboxed, cross-distro, auto-updating alternative to `apt` (bigger, slower, more secure by default).
- **Android**: runs Linux kernel, but NOT a GNU/Linux distro - different userspace (ART, Bionic, no GNU tools). AOSP = open base; Google Android/Fire OS/LineageOS/GrapheneOS/OEM variants all fork from AOSP.
- **pyenv**: manages multiple Python versions (`pyenv versions`, `pyenv install --list`, `pyenv global <version>`). Install separately on Windows AND WSL. Skip Anaconda (bloated) for data engineering use.

## Filesystem
- `ls` (list) / `ls -la` (long + hidden) | `pwd` (current path) | `whoami` (current user) | `echo "text"` (print/write) | `cat file` (print contents) | `nano file` (edit) | `clear` (wipe screen, session unaffected) vs `exit` (ends session) | `rm -rf` (delete, no undo - dangerous).
- `cd /` = root | `cd ~` = home | `cd ..` = parent dir | `cd .` = current dir | prompt format: `user@host:~$`.
- Root dirs: `/bin` (binaries), `/home` (user files), `/usr` (installed software), `/etc` (config), `/var` (logs/cache), `/opt` (3rd-party), `/tmp` (temp), `/boot` `/sys` (don't touch).

## Permissions
- Ownership != permission bits - owner can always restore their own permissions, even from `chmod 000`. Root bypasses permission checks entirely.
- Numeric: read=4, write=2, execute=1, summed per owner/group/other digit. `600`=owner rw | `700`=owner rwx | `644`=owner rw, group r, other r | `777`=everyone rwx (avoid).
- Symbolic: `u`/`g`/`o` + `+`/`-` + `r`/`w`/`x`. `chmod +x script.sh` = make executable (required before `./script.sh` works).
- User/group mgmt: `adduser`, `usermod -aG <group> <user>` (always `-aG` together), `groupadd`, `groups <user>`, `deluser`, `groupdel`.
- `sudo su` = persistent root session (Ctrl+D to exit). Only `sudo`-group users get sudo - deliberately restricted.

## grep / awk / sed
- Regex core: `.` any char | `*`/`+`/`?` repetition | `[abc]`/`[^abc]`/`[a-z]` classes | `^`/`$` anchors | `{n}`/`{n,m}` counts | `()` groups | `|` OR.
- `grep -E "pattern" file` (extended regex) | `grep -o` (extract match only) | `grep -i` (case-insensitive) | `grep -oE "[0-9]+"` (extract numbers).
- `awk -F, '{print $2}' file.csv` (print column 2) | `awk -F, '$3=="X"' file.csv` (filter rows).
- `sed 's/old/new/' file` (preview replace) | `sed -i 's/old/new/' file` (actually modify file).
- Python `re`: `re.search()` (first match) | `re.findall()` (all matches) | `re.sub()` (replace - PII masking) | `(?P<name>...)` named groups -> `.groupdict()`.
- Bash: `[[ $var =~ regex ]]` test, `${BASH_REMATCH[1]}` captured group.

## Processes
- `ps` / `ps aux | grep <name>` (list processes) | `<cmd> &` (background) | `nohup <cmd> &` (survives terminal close) | `jobs` (list background jobs, per-terminal) | `kill <PID>` (stop).
- `top`/`htop` (live resource view, `q` to quit) | `free` (memory) | `df` (disk space).

## cron
- `crontab -e` to edit. Syntax: `minute hour day month weekday` (`*` = every).
- `30 9 * * 1` = every Monday 9:30am. `* * * * *` = every minute.
- `#` comments out a job (disables without deleting). Apache Airflow uses the same 5-field syntax.

## Shell Automation & Operational Logs
- Shell script = list of terminal commands in a file, run in order. Starts with shebang `#!/bin/bash`.
- Needs `chmod +x script.sh` before `./script.sh` works (common first-time gotcha).
- Use case: provisioning a fresh server (install deps, clone repo, set env vars) in one execution.
- `systemctl status/start/stop/restart/enable/disable <service>` | `journalctl <service>` (view logs, `q` to exit pagination).

---

# Part 3: Flashcards

Q: Where was Unix developed, and what was its main issue?
A: Bell Labs (1969) - it was proprietary (cost money, closed source).

Q: What did GNU provide vs. what did Linux provide?
A: GNU (Stallman, 1983) provided nearly a full OS worth of tools (editor, compiler, shell) but no kernel. Linux (Torvalds, 1991) provided exactly that missing kernel.

Q: Why did GNU/Linux become popular with companies for data centers?
A: It was both open source AND completely free - no per-machine licensing cost, unlike proprietary Unix or Windows.

Q: What are the 3 major Linux distro families, and their package managers?
A: Debian (APT), Enterprise Linux (RPM/DNF/YUM), Arch (Pacman).

Q: What's the difference between apt and snap?
A: apt = lightweight, shares system libraries, distro-specific. snap = larger, self-contained/sandboxed, cross-distro, auto-updates, made by Canonical.

Q: Is Android a Linux distribution?
A: It runs the Linux kernel, but no - it's not a conventional GNU/Linux distro. Completely different userspace (ART, Bionic, no GNU tools).

Q: What does pyenv do, and what's the Windows/WSL gotcha?
A: Manages multiple Python versions on one machine. Install it separately in both Windows and WSL - the builds aren't interchangeable.

Q: What's the difference between `clear` and `exit`?
A: `clear` only wipes the visible screen (session/processes unaffected). `exit` actually ends the shell session.

Q: What does `~` mean in a terminal prompt?
A: Shorthand for your home directory (`/home/<username>`) - not the same as the root directory (`/`).

Q: What's in `/etc`, and what's in `/var`?
A: `/etc` = system configuration files (e.g. `/etc/hosts`). `/var` = files that change over time (logs, caches, backups).

Q: Is file ownership the same as having read/write permission?
A: No - separate concepts. Even with `chmod 000`, the owner can still change the file's permissions back to restore access.

Q: What do the digits in numeric chmod mean (e.g. 644)?
A: Read=4, write=2, execute=1, summed per digit for owner/group/other. 644 = owner read+write, group read, other read.

Q: Why does `./script.sh` fail right after creating a script?
A: New files aren't executable by default - run `chmod +x script.sh` first.

Q: Why is sudo access restricted to a specific group rather than given to everyone?
A: To limit the blast radius if a user makes a mistake or acts maliciously - not every user should have unrestricted super-user power on a shared system.

Q: What's the difference between grep, awk, and sed?
A: grep searches text, awk parses/selects structured row-and-column data, sed performs search-and-replace transformations.

Q: How do you make a sed replacement actually change the file (not just preview it)?
A: Use the `-i` flag: `sed -i 's/old/new/' file`.

Q: What does `awk -F,` do?
A: Sets the field delimiter to a comma, splitting each line into columns (`$1`, `$2`, etc.) like a SQL table.

Q: How do you run a command so it survives your terminal disconnecting?
A: `nohup <command> &` ("no hangup").

Q: What are the 5 fields in a cron schedule, in order?
A: Minute, hour, day (of month), month, weekday.

Q: What does `30 9 * * 1` mean in cron?
A: Every Monday at 9:30am.

Q: What tool used later in the course shares cron's exact scheduling syntax?
A: Apache Airflow.

Q: What must a shell script file start with, and what does it mean?
A: A shebang line, e.g. `#!/bin/bash` - tells the system which program should interpret the file.

Q: How do you check if a system service is running, and view its logs?
A: `systemctl status <service>` to check status; `journalctl <service>` to view logs (press `q` to exit paginated output).
