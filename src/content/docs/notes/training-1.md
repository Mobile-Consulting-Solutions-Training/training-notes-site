---
title: Training 1 - Linux and Shell Scripting
description: Unix/Linux background, Filesystem, Permissions, grep/awk/sed, and homework
---

Teacher: Evan Flint

Syllabus Day 2: Linux & Shell Scripting
Coverage: Filesystem, permissions, grep/awk/sed, processes, cron, shell automation and operational logs.

## Video Resources

| Video | Purpose | Link |
|---|---|---|
| 60 Linux Commands you NEED to know (in 10 minutes) | Rapid overview of 60 essential Linux terminal commands - good quick-reference companion to the Filesystem/Permissions/grep-awk-sed sections below | https://www.youtube.com/watch?v=gd7BXuUQ91w |

---

# Unix & Linux Background

Q. Where was Unix developed?

A. (Teacher's definition) Unix was developed at Bell Labs. Early Unix operating system had a filesystem and many commands that would look familiar to a modern Linux user.

Expanded: Unix originated in 1969 at Bell Labs (AT&T's research division), created by Ken Thompson, Dennis Ritchie, and others. It introduced foundational ideas still used today - a hierarchical filesystem, the "everything is a file" philosophy, small composable command-line tools piped together, and multi-user/multi-tasking support. Linux (created later by Linus Torvalds in 1991) is a separate, independently-written operating system kernel built to be Unix-like/POSIX-compliant - it's not Unix code itself, but follows the same design philosophy and command conventions. This lineage is why Linux still uses Unix-style commands, permissions, and filesystem structure today.

Q. What was the issue with Unix?

A. (Teacher's definition) Many found it useful, but it was proprietary.

Expanded: Unix was owned by AT&T and licensed commercially - different vendors (Sun's SunOS/Solaris, IBM's AIX, HP-UX, etc.) each built their own paid, closed-source Unix variants. This meant no one could freely use, inspect, or modify the source code, which fragmented the ecosystem and blocked wide, free adoption. This gap is exactly what motivated the creation of free/open alternatives - the GNU Project (Richard Stallman, 1983) aimed to build a free Unix-compatible operating system, and Linux (Linus Torvalds, 1991) provided the missing free kernel that, combined with GNU's tools, created a fully free and open Unix-like OS. This is why it's often called "GNU/Linux."

Q. Who created the Linux Kernel?

A. (Teacher's definition) The Linux Kernel was created by Linus Torvalds. But this was just the kernel - it wasn't an operating system that would be considered useful by a non-expert.

Expanded: Linus Torvalds created the Linux kernel in 1991 as a free, open-source, Unix-like alternative, released under the GPL license. Note the distinction: Linux itself is just the kernel (the core piece that manages hardware, memory, processes, and the filesystem) - what people call "Linux" as a full operating system (e.g. Ubuntu, Fedora, Debian) is really the Linux kernel combined with GNU tools and utilities, packaged by a "distribution" (distro). This is the free, open-source answer to Unix's proprietary licensing problem described above.

Q. Who created GNU, and what does it stand for?

A. (Teacher's definition) Another guy, named Richard Stallman, created a suite of tools including a graphic user interface, a text editor, a calculator, etc, with the intention of making an operating system out of the Linux kernel which could be more easily used by the general public. Stallman did not act alone - he was the leader of a foundation that did this called GNU. GNU is a recursive acronym - it stands for "GNU's Not Unix".

Expanded: Richard Stallman founded the GNU Project in 1983 (predating the Linux kernel by 8 years) with the goal of building a complete, free Unix-compatible operating system from scratch. By the early 1990s, GNU had produced nearly everything needed for a full OS - a text editor (Emacs), a compiler (GCC), a shell, a calculator, and other core utilities - except for one critical missing piece: a kernel. When Linus Torvalds released the Linux kernel in 1991, it filled exactly that gap. Combining the Linux kernel with GNU's existing suite of tools produced a complete, usable, free operating system - which is why it's technically "GNU/Linux," even though it's commonly just called "Linux."

| Term | Meaning |
|---|---|
| GNU | Recursive acronym: "GNU's Not Unix" - a self-referential joke common in hacker culture |
| GNU Project | Founded by Richard Stallman in 1983, aimed to build a free Unix-compatible OS |
| What GNU built | User-facing tools/applications: text editor, compiler, shell, calculator, GUI components, etc. |
| What GNU was missing | A kernel - the low-level core that talks to hardware |
| What Linux provided | Exactly that missing kernel (1991) |
| GNU + Linux | Combined = a complete, free, usable operating system ("GNU/Linux") |

Q. Why did GNU/Linux become popular with companies?

A. (Teacher's definition) Because it was not only open source, but also completely free, it became a very attractive option for companies who wanted an operating system to use in their data centers.

Expanded: Proprietary Unix variants (Solaris, AIX, HP-UX) required per-machine/per-seat licensing fees - expensive at data center scale, where a company might run thousands of servers. GNU/Linux offered the same Unix-like capabilities (multi-user, multi-tasking, scriptable, stable) with zero licensing cost and no vendor lock-in, since the source code itself was freely available to inspect, modify, and redistribute. This combination (free + open source) made it the default choice for server/data center infrastructure, which is exactly why Linux underlies the vast majority of servers, cloud infrastructure, and - relevant to this course - Big Data tooling (Hadoop, Spark, Kafka, etc. all run on Linux).

Q. What is a Linux Distribution?

A. (Teacher's definition) A Linux Distribution is a variety of linux developed by an organization with a particular design philosophy.

Expanded: Since the Linux kernel and GNU tools are both free/open, different organizations package them together differently - bundling the kernel, GNU utilities, a package manager, default software, and configuration choices into a ready-to-install OS ("distro"). Each distro reflects different priorities: some optimize for server stability, some for ease of use, some for security, some for full user control. This is why "Linux" isn't one single OS you download - it's a family of related operating systems all built on the same kernel.

| Distribution | Design philosophy / focus |
|---|---|
| Ubuntu | The version most of the class is probably using (installed by default via WSL). Generally considered the most flexible major distro, and a good pick if you're new - widely used for both desktops and servers |
| Debian | Stability and free software principles - the base many other distros build on |
| Red Hat Enterprise Linux (RHEL) | Enterprise-focused, paid support, common in corporate data centers |
| CentOS / Rocky Linux / AlmaLinux | Free, RHEL-compatible alternatives (common in production servers) |
| Amazon Linux | AWS's own distro, optimized for EC2 |
| Arch Linux | Minimal, highly configurable, for users who want full control |
| Zorin OS | Designed to look/feel as close to Windows as possible - good for beginners transitioning from Windows |

Q. What are the broad categories (families) of Linux distributions?

A. (Teacher's definition)
- The first broad category of Linux distributions is called Debian.
- The other major category of distributions is called Enterprise Linux. Enterprise distributions include Red Hat, Fedora, and CentOS.
- The third major category of distributions is Arch Linux. Arch Linux is for the hardcore developer who insists on full and complete control of their machine, and wants to make all the small scale decisions about how that machine operates.

Expanded: Rather than being one flat list, Linux distributions group into a few broad "families" - each family shares a common lineage, package manager, and conventions, and other distros are usually built on top of (or derived from) one of these base families. Debian is the first/foundational family covered - Ubuntu, Zorin OS, and many others are themselves built on top of Debian, inheriting its package manager (APT/`.deb` packages) and conventions. Enterprise Linux is the other major family, centered on Red Hat - built for stability and long-term support, common in corporate/enterprise data centers (hence the name). Arch Linux is the third major family - known for a minimal, do-it-yourself philosophy and its rolling-release model (continuous updates rather than fixed version releases).

| Distro Family | Package format/manager | Notable members |
|---|---|---|
| Debian | `.deb` / APT | Debian itself, Ubuntu, Zorin OS, Linux Mint, Kali Linux |
| Enterprise Linux | `.rpm` / RPM (DNF/YUM) | Red Hat Enterprise Linux (RHEL), Fedora, CentOS |
| Arch Linux | Pacman | Arch Linux itself, Manjaro, EndeavourOS |

(More families may exist - e.g. SUSE - but Debian, Enterprise Linux, and Arch are the three major categories covered in class.)

Q. What is a package manager?

A. (Teacher's definition) A package manager is a tool, usually but not always used on the command line, which provides a simple way to download and install software packages.

Expanded: Instead of manually downloading, compiling, and installing software (and its dependencies) yourself, a package manager automates that - it fetches the requested software (and anything it depends on) from a repository, installs it in the right place, and can update or remove it later. Each distro family has its own package manager, tied to its package format (see the Distro Family table above).

| Distro Family | Package Manager | Example commands |
|---|---|---|
| Debian (Ubuntu, Zorin, Mint, Kali) | APT, also called apt-get (`.deb`) | `apt install <package>`, `apt update`, `apt upgrade` (older/more specific form: `apt-get install <package>`) |
| Enterprise Linux (Red Hat, Fedora, CentOS) | RPM (Red Hat Package Manager) | `rpm -i <package>.rpm` (higher-level: `dnf install <package>` / `yum install <package>`) |
| Arch | Pacman | `pacman -S <package>` |

Note: `apt` is the newer, simplified command-line tool; `apt-get` is the older, more granular tool it was built on top of. Both still work on Debian-family systems - `apt` is generally recommended for everyday interactive use.

Note: Similarly, RPM is the original/underlying package manager for Enterprise Linux (also the name of the `.rpm` package format itself); DNF (and its predecessor YUM) are higher-level tools built on top of RPM that handle dependency resolution automatically - similar to how apt is built on top of the lower-level dpkg for Debian.

Q. What is the difference between `sudo apt` and `snap`?

A. Both are ways to install software on Ubuntu, but they work very differently under the hood.

| | `apt` | `snap` |
|---|---|---|
| Package format | `.deb` - Debian-specific | `.snap` - universal, works across many distros |
| Dependencies | Shared with the system (uses existing system libraries) | Bundled inside the package itself (self-contained) |
| Install size | Smaller - reuses what's already installed | Larger - ships its own dependencies every time |
| Isolation | Runs directly on the system, no sandboxing | Runs sandboxed/confined (more secure by default) |
| Startup speed | Fast | Slightly slower (unpacking/mounting the sandboxed package) |
| Maintained by | The Debian/Ubuntu package repositories generally | Canonical (Ubuntu's parent company) - its own system |
| Updates | Managed manually (`apt update && apt upgrade`) | Auto-updates by default in the background |
| Example command | `sudo apt install <package>` | `sudo snap install <package>` |

Bottom line: `apt` is the traditional, lightweight, distro-native package manager - what you'd use for most things. `snap` is Canonical's newer universal packaging system - trades some size/speed for cross-distro compatibility, sandboxing, and easier auto-updates. Both can coexist on the same Ubuntu system; some software is only available via one or the other.

---

Q. Is Android part of the Linux family?

A. Yes - but with an important qualification. Android runs on an actual Linux kernel, but it is NOT a conventional GNU/Linux distribution like Ubuntu, Fedora, or Arch. It shares the Linux kernel as its foundation, but builds a completely different userspace on top of it (no GNU tools, no glibc, different runtime/framework).

Android's stack (simplified):

```
Android Apps (Kotlin / Java / Native C++)
Android Framework APIs
Android Runtime (ART)
System Services / Native Libraries (Binder, Bionic libc, SELinux, etc.)
Hardware Abstraction Layer (HAL)
Linux Kernel (scheduling, memory, drivers, networking, processes, security)
Hardware
```

Compare to a conventional distro like Ubuntu:

| | Ubuntu (conventional GNU/Linux) | Android |
|---|---|---|
| Kernel | Linux kernel | Linux kernel (Google's "Android Common Kernel" - upstream Linux LTS + Android-specific patches) |
| Core libraries | GNU utilities, glibc, systemd | Bionic libc, Binder, HAL (Android-specific, not GNU) |
| Runtime/framework | Standard shell/apps run directly on the OS | Android Runtime (ART) + Android Framework APIs sit between apps and the kernel |
| Apps | Native binaries via shell/package manager | Kotlin/Java/Native C++ apps via ART |

Note: Google previously dealt with heavy kernel fragmentation (manufacturers customizing kernels per device, sometimes 50%+ out-of-tree code) - the Generic Kernel Image (GKI) architecture standardizes this across devices.

Key distinction - AOSP vs "Google's Android": The Android Open Source Project (AOSP) is the open-source, freely modifiable base ("a complete and fully functional implementation of the Android mobile platform" per Google). Google's own consumer product adds a proprietary layer on top - Play Store, Gmail, Maps, Google Play Services, Google APIs - which is NOT part of AOSP. Because AOSP is open and modifiable, this split has enabled major derivatives:

| AOSP Derivative | What it is |
|---|---|
| Google Android (Pixel, etc.) | AOSP + Google's proprietary layer (Play Store, GMS, Google apps) |
| Samsung One UI, Xiaomi HyperOS, other OEM variants | AOSP + OEM customization, usually still with Google services (outside markets like mainland China) |
| Amazon Fire OS | AOSP forked into Amazon's own ecosystem (Amazon Appstore, Alexa, Amazon accounts) instead of Google's - powers 250M+ Fire TV devices |
| LineageOS (successor to CyanogenMod) | Community-built replacement OS from AOSP + device-specific code - keeps older/abandoned phones updated |
| GrapheneOS | AOSP hardened for privacy/security (sandboxing, exploit mitigations, optional/sandboxed Google Play) while keeping Android app compatibility |
| Chinese Android variants | AOSP-derived, with Google's layer largely replaced by domestic services/stores/cloud (since Google services are largely absent in mainland China) |

Genealogy:

```
Linux kernel project
        |
   +----+----------------------+
   |                            |
GNU/Linux                    Android
(Debian, Fedora, Arch...)       |
                               AOSP
                                |
        +----------+-----------+-----------+
        |          |           |           |
   Google Android  Fire OS  LineageOS  GrapheneOS
        |
  OEM variants (Samsung, Xiaomi, etc.)
```

The key nuance: Android isn't descended from Debian/Ubuntu/GNU-Linux - Android and conventional distros just share the Linux kernel as a common foundation, then build very different userspaces on top of it. This is also why anyone can, in principle, build their own OS on the AOSP+Linux foundation while retaining compatibility with the existing Android APK app ecosystem - which is the same underlying strategy Android Automotive OS uses for cars: take the proven Linux/AOSP foundation instead of building a low-level OS and app framework from scratch, then customize heavily on top (conceptually similar to what Amazon did with Fire OS, just for vehicles instead of tablets/TVs).

---

Q. What is pyenv, and how do I install it?

A. (Teacher's definition) pyenv is a tool for managing multiple Python versions on one machine, so you can switch between them per-project instead of being stuck with one system-wide Python version.

- Linux and Mac: https://github.com/pyenv/pyenv
- Windows: https://github.com/pyenv-win/pyenv-win - there is a single command that can be copied and pasted to install it, but you must open PowerShell (NOT cmd) in Administrator mode. Even then, on some systems there will be an additional layer of security to get past - ask if you run into it.

| Platform | Repo | Notes |
|---|---|---|
| Linux / Mac | github.com/pyenv/pyenv | The main version of pyenv |
| Windows | github.com/pyenv-win/pyenv-win | Separate Windows-specific port - install via PowerShell (Administrator mode required, not cmd) |

---

# Filesystem

Q. What does `ls` do?

A. Lists the contents of a directory - files and subdirectories.

| Flag | What it does |
|---|---|
| `ls` | List names in the current directory |
| `ls -l` | Long format - permissions, owner, size, modified date |
| `ls -a` | Show hidden files too (names starting with `.`) |
| `ls -la` | Combine both - long format + hidden files |
| `ls -lh` | Long format with human-readable sizes (KB/MB/GB instead of raw bytes) |
| `ls -R` | Recursive - list subdirectories' contents too |
| `ls -t` | Sort by modification time (newest first) |
| `ls <path>` | List contents of a specific directory instead of the current one |

---

Q. What does `pwd` do?

A. Prints the full absolute path of the directory you're currently in (print working directory) - tells you exactly where you are in the filesystem.

```
$ pwd
/home/student/projects
```

---

Q. What does `whoami` do?

A. Prints the username you're currently logged in as.

```
$ whoami
student
```

---

Q. What does `echo` do?

A. Prints text (or the value of a variable) to the terminal.

```
$ echo "Hello, world"
Hello, world

$ echo $HOME
/home/student

$ echo "Path is: $PATH"
Path is: /usr/local/bin:/usr/bin:/bin
```

Also commonly used to write text into a file (with `>` or `>>`):
```
$ echo "some text" > file.txt      # overwrite file.txt with "some text"
$ echo "more text" >> file.txt     # append "more text" to file.txt
```

---

Q. What does `cat` do?

A. Prints the contents of one or more files to the terminal (con**cat**enate).

```
$ cat file.txt
(contents of file.txt printed here)

$ cat file1.txt file2.txt
(prints file1 then file2, concatenated)

$ cat file1.txt file2.txt > combined.txt
(combines both files into a new file)
```

---

Q. What does `nano` do?

A. A simple, beginner-friendly terminal-based text editor - lets you open and edit a file directly in the terminal (unlike `cat`, which only displays content, `nano` lets you change it).

```
$ nano file.txt
```

Common shortcuts (shown at the bottom of the nano screen): `Ctrl+O` (save/"write out"), `Ctrl+X` (exit), `Ctrl+K` (cut a line), `Ctrl+U` (paste).

---

Q. What does `clear` do, and how does it differ from `exit`/`quit`?

A. `clear` wipes the visible terminal screen - a clean, empty prompt. It does NOT end the session, close any program, or affect anything running - purely visual.

```
$ clear
(screen wipes, you're left with a fresh empty prompt, still in the same shell/directory/session)
```

`exit` (or `Ctrl+D`) actually terminates the current shell session or program.

| | `clear` | `exit` |
|---|---|---|
| What it does | Wipes the visible screen | Terminates the current shell/program |
| Session state | Unaffected - still logged in, same directory, same running processes | Session ends - logged out (or the program closes) |
| Reversible? | Yes - just keep working | No - have to start a new session |

Note: `quit` isn't a universal shell command like `exit` - it's context-dependent (e.g. `nano` uses `Ctrl+X`, `less`/`man` use `q`, some programs define their own `quit`). `exit` is the standard command for leaving a shell itself.

---

Q. What does `cd /` do?

A. (Teacher's definition) `cd /` is for the root directory.

Expanded: `cd` (change directory) moves you to a different directory - `cd /` specifically takes you to the root directory, the top of the entire filesystem tree that everything else branches from.

| Command | Where it goes |
|---|---|
| `cd /` | Root directory - the top of the filesystem |
| `cd` or `cd ~` | Your home directory |
| `cd ..` | Up one level (parent directory) |
| `cd -` | Back to the previous directory you were in |
| `cd <path>` | A specific directory (relative or absolute path) |

---

Q. What does `rm` do?

A. Deletes files (and, with a flag, directories). Unlike a GUI trash/recycle bin, there's no undo - deleted files are gone immediately.

| Flag | What it does |
|---|---|
| `rm file.txt` | Delete a single file |
| `rm file1.txt file2.txt` | Delete multiple files at once |
| `rm -r <directory>` | Recursively delete a directory and everything inside it |
| `rm -f <file>` | Force delete, no confirmation prompt (even for write-protected files) |
| `rm -rf <directory>` | Recursive + force - deletes a whole directory tree with no prompts |

Warning: `rm -rf` is one of the most dangerous commands in Linux - no confirmation, no recovery. Running it on the wrong path (especially something like `rm -rf /` or `rm -rf *` in the wrong directory) can wipe out far more than intended. Always double-check the path before running it, especially with `-f`.

---

# Permissions

Q. Is file ownership separate from having read/write permission on a file?

A. (Teacher's definition) Yes. This is a useful distinction in Linux: being the owner of a file and having permission to read/write the file are separate concepts.

Demonstration:
```
$ echo "important data" > test.txt
$ chmod 000 test.txt
$ ls -l test.txt
---------- 1 evan evan ... test.txt
```

At this point, as a normal process running as `evan`:
```
$ cat test.txt
cat: test.txt: Permission denied

$ echo "new data" > test.txt
-bash: test.txt: Permission denied
```

However, the owner is allowed to change the file's permission bits, even though they currently have no read/write/execute permission on the file. So you can simply restore your own permissions:
```
$ chmod 600 test.txt
$ ls -l test.txt
-rw------- 1 evan evan ... test.txt

$ echo "new data" > test.txt    # now works
```

Key distinction: `chmod 000` means "nobody gets ordinary read/write/execute access." It does NOT mean "the owner loses ownership or the ability to change the permissions."

Another wrinkle: `root` can generally bypass ordinary Unix file permission checks. So even while the file is `000`, root can still do:
```
$ sudo cat test.txt
$ sudo nano test.txt
$ sudo chmod 600 test.txt
```

A good demonstration sequence:
```
touch locked.txt
chmod 000 locked.txt
ls -l locked.txt

cat locked.txt               # Permission denied
echo hello > locked.txt      # Permission denied

chmod u+rw locked.txt        # Owner can restore permissions

echo hello > locked.txt      # Works
cat locked.txt               # Works
```

Note: there's a subtle distinction with deleting a file - deletion is primarily controlled by the permissions on the containing directory, not the file itself. So a `chmod 000 locked.txt` file can often still be deleted by its owner if they have sufficient permissions on the directory containing it.

# grep / awk / sed

Q. What is a regular expression (regex)?

A. A pattern for finding, validating, extracting, or replacing text. The core regex concepts are the same across Linux tools and Python - only the syntax/API used to invoke them differs. `grep`, `sed`, and `awk` are the tools that actually do the matching; the shell itself doesn't perform regex matching.

## Core regex syntax

| Pattern | Meaning | Example |
|---|---|---|
| `.` | Any single character | `c.t` matches `cat`, `cot` |
| `*` | Previous item 0 or more times | `ab*` matches `a`, `ab`, `abb` |
| `+` | Previous item 1 or more times | `ab+` matches `ab`, `abb` |
| `?` | Previous item 0 or 1 time | `colou?r` |
| `[abc]` | One character from the set | `[abc]at` |
| `[^abc]` | Anything except these | `[^0-9]` |
| `[a-z]` | Character range | `[A-Z]` |
| `\d` | Digit (Python/Perl-style) | `\d+` |
| `\w` | Word character | `\w+` |
| `\s` | Whitespace | `\s+` |
| `^` | Beginning of line/string | `^ERROR` |
| `$` | End of line/string | `ERROR$` |
| `{3}` | Exactly 3 repetitions | `[0-9]{3}` |
| `{2,5}` | Between 2 and 5 repetitions | `[0-9]{2,5}` |
| `(...)` | Group | `(ERROR\|WARNING)` |
| `\|` | OR (regex flavor dependent) | `cat\|dog` |

Key point: `*`, `+`, and `?` modify whatever comes immediately before them - e.g. `[0-9]+` means "one or more digits."

## grep

```
grep "ERROR" application.log              # basic search
grep -i "error" application.log           # case insensitive
grep "^ERROR" application.log             # lines starting with ERROR
grep "ERROR$" application.log             # lines ending with ERROR
```

Use `grep -E` (extended regex) so operators like `+`, `?`, `{}`, and `|` work naturally:
```
grep -E "ERROR|WARNING" application.log   # ERROR OR WARNING
grep -E "[0-9]+" application.log          # lines with numbers
grep -E "[0-9]{3}" application.log        # lines with a 3-digit number
```

`grep -o` extracts only the matching text (useful for demonstrations):
```
# Given: customer_id=38291 status=ACTIVE
grep -oE "customer_id=[0-9]+" demo.txt    # -> customer_id=38291
grep -oE "[0-9]+" demo.txt                # -> 38291
```

Character classes:
```
grep -E "[A-Z]+" demo.txt          # uppercase letters
grep -E "[a-z]+" demo.txt          # lowercase letters
grep -E "[0-9]+" demo.txt          # numbers
grep -E "[0-9A-Fa-f]+" demo.txt    # hex-looking values
```

Negated character classes - `^` means something different inside `[...]`:
```
grep -oE "[^0-9]+" demo.txt        # anything that is NOT a digit
```

## Regex in Bash scripts

The `=~` operator checks if a string matches a regex:
```bash
value="customer_12345"
if [[ $value =~ ^customer_[0-9]+$ ]]; then
    echo "Valid customer ID"
else
    echo "Invalid customer ID"
fi
```

Bash exposes captured regex groups through `BASH_REMATCH`:
```bash
value="customer_12345"
if [[ $value =~ customer_([0-9]+) ]]; then
    echo "Complete match: ${BASH_REMATCH[0]}"
    echo "Customer number: ${BASH_REMATCH[1]}"
fi
# Complete match: customer_12345
# Customer number: 12345
```
The parentheses `([0-9]+)` create a capture group.

## Regex in Python (the `re` module)

`re.search()` - find a pattern anywhere in a string:
```python
import re
text = "Customer number is 83921"
match = re.search(r"[0-9]+", text)
if match:
    print(match.group())   # 83921
```
Note the `r` prefix - a raw string, generally preferable for regex since backslashes aren't interpreted by Python's normal string parser first.

`re.findall()` - one of the most useful functions for data engineering:
```python
import re
text = """
customer_id=123
customer_id=456
customer_id=789
"""
ids = re.findall(r"customer_id=([0-9]+)", text)
print(ids)   # ['123', '456', '789']
```

`re.sub()` - find and replace (useful for PII masking/data cleansing):
```python
import re
text = "Customer SSN: 123-45-6789"
cleaned = re.sub(r"[0-9]{3}-[0-9]{2}-[0-9]{4}", "***-**-****", text)
print(cleaned)   # Customer SSN: ***-**-****
```

Shorthand character classes in Python:
```python
re.findall(r"\d+", text)      # \d = digit
re.findall(r"\w+", text)      # \w = letters, digits, underscore (Unicode-aware)
re.split(r"\s+", text)        # \s = whitespace

re.split(r"\s+", "Spark     Kafka   Hadoop")
# ['Spark', 'Kafka', 'Hadoop']
```

Practical email validation example:
```python
import re
email = "evan@example.com"
pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
if re.match(pattern, email):
    print("Looks like an email")
```
Breaking it down: `^` (start) `[A-Za-z0-9._%+-]+` (local part) `@` `[A-Za-z0-9.-]+` (domain) `\.` (literal dot) `[A-Za-z]{2,}` (TLD, 2+ letters) `$` (end).

Named capture groups - turns unstructured text into structured data:
```python
import re
log = "2026-09-11 ERROR server=db01 message=connection_failed"
pattern = (
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<level>\w+) "
    r"server=(?P<server>\w+) "
    r"message=(?P<message>\w+)"
)
match = re.search(pattern, log)
if match:
    print(match.groupdict())
# {'date': '2026-09-11', 'level': 'ERROR', 'server': 'db01', 'message': 'connection_failed'}
```

## Shell vs Python - the same pattern, different tools

Given `customer_id=10023`, the conceptual regex `customer_id=([0-9]+)` looks like this across tools:

| Tool | Code |
|---|---|
| Bash | `[[ $line =~ customer_id=([0-9]+) ]] && echo "${BASH_REMATCH[1]}"` |
| Python | `re.search(r"customer_id=([0-9]+)", line).group(1)` |
| grep | `grep -oE "customer_id=[0-9]+" demo.txt` |

The key idea: regex is the pattern language - Bash, grep, Python, sed, Spark, databases, IDEs, etc. are just different ways of applying that same language.

Learning priority for beginners: `[0-9]`, `[A-Za-z]`, `.`, `*`, `+`, `^`, `$`, `{n}`, `[^...]`, groups, and `|` first - then practice them via `grep -E`, Bash `=~`, and Python's `re.search`/`re.findall`/`re.sub`.

---

# Homework Assignment: Linux Users, Permissions, Text Processing & Processes

## Objective

Practice the Linux commands covered in class, including user management, file permissions, `grep`, `awk`, `sed`, shell scripting, process management, and `systemctl`.

Complete each exercise from the Linux terminal. For each exercise, submit the commands used and the resulting terminal output.

## Exercises

1. **Create and manage a user**
   Create a new Linux user named `data_student`. Verify that the user exists using an appropriate command. Create a group named `data_team` and add `data_student` to that group. Display the user's UID, GID, and group memberships.

2. **Practice file permissions**
   Create a file named `confidential.txt` containing at least one line of text. Change its permissions so that the owner can read and write it, the group can only read it, and everyone else has no permissions. Display the resulting permissions with `ls -l`. Do this using numeric `chmod` notation.

3. **Practice symbolic `chmod`**
   Create a shell script named `hello.sh` that prints `Hello from Linux!`. Attempt to execute it before giving it execute permission. Then use symbolic `chmod` notation to give the owner execute permission and successfully run the script.

4. **Search data with `grep`**
   Create a file called `application.log` containing at least 10 lines. At least three lines should contain `ERROR`, two should contain `WARNING`, and the others should contain `INFO`. Use `grep` to:
   - Find all `ERROR` lines.
   - Find both `ERROR` and `WARNING` lines using one command.
   - Count the number of lines containing `ERROR`.

5. **Process CSV data with `awk`**
   Create `employees.csv` with this structure and at least six employees:
   ```
   id,name,department,salary
   1,Alice,Engineering,95000
   2,Bob,Sales,72000
   ```
   Use `awk` to display only employee names and salaries. Then use another `awk` command to display only employees earning more than $80,000.

6. **Transform data with `sed`**
   Using your `employees.csv` file, use `sed` to replace every occurrence of `Engineering` with `Technology`. First display the transformed data without changing the original file. Then create a backup and use `sed` to make the change in the actual file.

7. **Create a system-information shell script**
   Create a script named `system_report.sh` that prints:
   - Current username
   - Current date and time
   - Current working directory
   - Available disk space
   - Memory usage
   - System uptime

   Give the script appropriate execute permissions and run it using `./system_report.sh`.

8. **Investigate running processes**
   Start the following process in the background: `sleep 500 &`. Find its PID using `ps` or `pgrep`. Verify that it is running, terminate it using `kill`, and then demonstrate that the process no longer exists.

9. **Foreground and background jobs**
   Start `sleep 1000`. Suspend the process using the appropriate keyboard shortcut. Use `jobs` to display it, resume it in the background, use `jobs` again to verify its status, bring it back to the foreground, and finally terminate it.

10. **Investigate a system service**
    Choose an existing systemd service on your machine, such as `ssh`, `cron`, or `docker`. Use `systemctl` to determine:
    - Whether the service is running.
    - Whether it is enabled at boot.
    - The service's main PID, if running.

    Then use `journalctl` to display the most recent 10 log entries for that service.

    Do not disable or permanently modify an important system service.

## Submission

Submit a single text or Markdown file named `linux_homework_<your_name>.txt`.

For each exercise include:
```
Exercise 1

Commands:
<commands you used>

Output:
<relevant terminal output>

Explanation:
<1-3 sentences explaining what the commands did>
```

The goal is not simply to get the expected output. You should be able to explain why the command worked and what its important options mean.

