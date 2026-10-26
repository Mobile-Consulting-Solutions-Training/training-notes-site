---
title: "Training 0 Homework"
description: "Homework assignment for Training 0: Data Engineering Fundamentals."
sidebar:
  order: 0
---

:::note
The assignment prompt as given in class. Related notes: [Training 0](/training-notes-site/notes/training-0/).
:::

## Prerequisites for Next Session

The assignment covers both Mac and Windows: Mac users follow the macOS guide, Windows users the Windows guide below it.

### macOS Setup Guide: Hardware Virtualization + Docker

For Mac users, setup is simpler than Windows - WSL is not required because macOS is Unix-based. You only need to verify your Mac supports virtualization and install Docker Desktop.

#### 1. Hardware virtualization on Mac

Apple Silicon Macs (M1, M2, M3, M4, M5, etc.): virtualization support is built into the processor and macOS - there is normally no BIOS/UEFI setting to enable. Check your chip: Apple menu -> About This Mac -> look for "Chip" (e.g. "Chip: Apple M3 Pro"). If it's Apple M1-M5 or another Apple Silicon chip, proceed directly to installing Docker.

Intel Macs: open Terminal and run:
```
sysctl -a | grep machdep.cpu.features
```
Look for `VMX` in the output - this indicates the Intel processor supports Intel VT-x hardware virtualization. You can also run:
```
sysctl -n machdep.cpu.features | grep VMX
```
Unlike a typical Windows PC, Macs generally don't provide a BIOS setting to manually enable Intel VT-x - on supported Intel Macs, macOS manages virtualization capability itself.

#### 2. Determine whether you need Apple Silicon or Intel Docker

Apple menu -> About This Mac -> look at Chip/Processor:
- Apple M1/M2/M3/M4/M5 -> download the Apple Silicon version of Docker Desktop
- Intel Core i5/i7/i9 -> download the Intel version

#### 3. Install Docker Desktop

- [ ] Download Docker Desktop for Mac (correct version for your chip): https://docs.docker.com/desktop/setup/install/mac-install/
- [ ] Open the .dmg, drag Docker into the Applications folder
- [ ] Open Applications, launch Docker
- [ ] Accept the license agreement, allow any macOS permissions requested, enter your Mac password if prompted
- [ ] Wait for Docker to start (may take a minute)

#### 4. Verify Docker

- [ ] In Terminal:
```
docker --version
docker compose version
docker run hello-world
```
Should print "Hello from Docker!" after downloading the test image.

#### 5. Test with a Linux container

- [ ] Run:
```
docker run -it ubuntu bash
cat /etc/os-release
exit
docker ps -a
docker images
```

If `docker run hello-world` and the Ubuntu container both work, the Mac is ready for Docker-based development.

### Windows Setup Guide (WSL 2 + Docker Desktop)

Recommended Windows configuration: Windows -> WSL 2 -> Ubuntu -> Docker Desktop. WSL 2 uses hardware virtualization, so virtualization should be checked before installing the rest of the environment.

1. Check hardware virtualization: Task Manager (Ctrl+Shift+Esc) -> Performance -> CPU -> look for "Virtualization: Enabled"
2. If disabled, enable it in BIOS/UEFI (Windows 11: Settings -> System -> Recovery -> Advanced startup -> Restart now -> Troubleshoot -> Advanced options -> UEFI Firmware Settings). Look for "Intel VT-x"/"Intel Virtualization Technology" (Intel) or "SVM Mode"/"AMD-V" (AMD), set to Enabled, save and restart.
3. Install WSL: open PowerShell as Administrator, run `wsl --install` (installs WSL 2, the Linux kernel, and Ubuntu by default). Restart when prompted.
4. Complete Ubuntu setup: launch Ubuntu from Start menu, set a Linux username/password (separate from Windows credentials; password won't show characters as you type).
5. Verify WSL 2: `wsl --status` and `wsl --list --verbose` - should show Ubuntu with VERSION 2. If it shows version 1, run `wsl --set-version Ubuntu 2` and `wsl --set-default-version 2`. Keep it updated with `wsl --update` (Docker requires at least WSL 2.1.5).
6. Update Ubuntu: `sudo apt update` then `sudo apt upgrade -y`. Optionally `sudo apt install -y curl wget git unzip`. Verify with `uname -a`.
7. Install Docker Desktop for Windows (don't install Docker Engine separately inside Ubuntu - use Docker Desktop's WSL 2 integration instead): download from docs.docker.com/desktop/setup/install/windows-install, run the installer, select the WSL 2 backend when prompted.
8. Configure Docker: Docker Desktop -> Settings -> General -> ensure "Use the WSL 2 based engine" is enabled; Settings -> Resources -> WSL Integration -> enable integration with Ubuntu.
9. Verify Docker from the Ubuntu terminal: `docker --version`, `docker compose version`, `docker run hello-world` (should print "Hello from Docker!").
10. Test a real container: `docker run -it ubuntu bash`, then `cat /etc/os-release`, `exit`, `docker ps -a`, `docker images`.

Final verification (from PowerShell then Ubuntu): `wsl --status` / `wsl --list --verbose` (Ubuntu should show VERSION 2), then `git --version`, `docker --version`, `docker compose version`, `docker run hello-world` - all four should work.
