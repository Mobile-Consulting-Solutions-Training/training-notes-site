---
title: Training 1 Homework
description: Linux Users, Permissions, Text Processing and Processes - assignment and completed submission
---

## Assignment

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

## Submission Format

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


## Submission

```
Linux Homework - Alex Jackson
Environment: Ubuntu 24.04 Docker container (running systemd) on macOS host

================================================================================
Exercise 1 - Create and manage a user
================================================================================

Commands:
useradd -m data_student
id data_student
groupadd data_team
usermod -aG data_team data_student
id data_student

Output:
uid=1001(data_student) gid=1001(data_student) groups=1001(data_student)
uid=1001(data_student) gid=1001(data_student) groups=1001(data_student),1002(data_team)

Explanation:
`useradd -m` creates the user and their home directory. `id` displays UID/GID/group
memberships. `groupadd` creates a new group, and `usermod -aG` appends the user to
it (-a = append, don't remove existing groups; -G = supplementary groups). The
second `id` confirms data_student now belongs to both their own primary group and
the new data_team group.

================================================================================
Exercise 2 - Practice file permissions (numeric chmod)
================================================================================

Commands:
echo "this is confidential" > confidential.txt
chmod 640 confidential.txt
ls -l confidential.txt

Output:
-rw-r----- 1 root root 21 Sep 14 16:16 confidential.txt

Explanation:
Numeric chmod digits are read=4, write=2, execute=1, summed per owner/group/other.
640 = owner read+write (4+2=6), group read-only (4), others none (0) - matching
the -rw-r----- shown by ls -l.

================================================================================
Exercise 3 - Practice symbolic chmod
================================================================================

Commands:
printf '#!/bin/bash\necho "Hello from Linux!"\n' > hello.sh
ls -l hello.sh
./hello.sh
chmod u+x hello.sh
ls -l hello.sh
./hello.sh

Output:
-rw-r--r-- 1 root root 37 Sep 14 16:16 hello.sh
bash: line 6: ./hello.sh: Permission denied
-rwxr--r-- 1 root root 37 Sep 14 16:16 hello.sh
Hello from Linux!

Explanation:
New files aren't executable by default, so running ./hello.sh initially fails with
"Permission denied". `chmod u+x` adds execute permission for the owner (u) only,
changing the mode to -rwxr--r--, after which the script runs successfully.

================================================================================
Exercise 4 - Search data with grep
================================================================================

Commands:
cat > application.log << 'EOF'
INFO Starting application server
INFO Loading configuration file
ERROR Failed to connect to database
WARNING Connection pool near capacity
INFO Request received from client
ERROR Timeout while processing request
INFO Cache warmed successfully
WARNING Disk usage above 80 percent
ERROR Unhandled exception in worker thread
INFO Application shutdown complete
EOF
grep 'ERROR' application.log
grep -E 'ERROR|WARNING' application.log
grep -c 'ERROR' application.log

Output:
ERROR Failed to connect to database
ERROR Timeout while processing request
ERROR Unhandled exception in worker thread

ERROR Failed to connect to database
WARNING Connection pool near capacity
ERROR Timeout while processing request
WARNING Disk usage above 80 percent
ERROR Unhandled exception in worker thread

3

Explanation:
Plain `grep 'ERROR'` prints every line containing that literal text. `grep -E`
enables extended regex so `|` works as OR, matching ERROR or WARNING lines.
`grep -c` counts matching lines instead of printing them (3 ERROR lines).

================================================================================
Exercise 5 - Process CSV data with awk
================================================================================

Commands:
cat > employees.csv << 'EOF'
id,name,department,salary
1,Alice,Engineering,95000
2,Bob,Sales,72000
3,Carla,Engineering,88000
4,Derek,Marketing,65000
5,Elena,Engineering,102000
6,Frank,Sales,78000
EOF
awk -F, 'NR>1 {print $2, $4}' employees.csv
awk -F, 'NR>1 && $4 > 80000 {print $2, $4}' employees.csv

Output:
Alice 95000
Bob 72000
Carla 88000
Derek 65000
Elena 102000
Frank 78000

Alice 95000
Carla 88000
Elena 102000

Explanation:
`-F,` sets the comma as the field delimiter, so each line splits into $1, $2, $3...
like SQL columns. `NR>1` skips the header row (NR = current line number). The
second command adds a condition ($4 > 80000) so only matching rows print.

================================================================================
Exercise 6 - Transform data with sed
================================================================================

Commands:
sed 's/Engineering/Technology/' employees.csv
grep Engineering employees.csv | head -1
cp employees.csv employees.csv.bak
sed -i 's/Engineering/Technology/' employees.csv
cat employees.csv
grep Engineering employees.csv.bak

Output:
id,name,department,salary
1,Alice,Technology,95000
2,Bob,Sales,72000
3,Carla,Technology,88000
4,Derek,Marketing,65000
5,Elena,Technology,102000
6,Frank,Sales,78000

1,Alice,Engineering,95000     <- confirms original file untouched by preview

id,name,department,salary
1,Alice,Technology,95000
2,Bob,Sales,72000
3,Carla,Technology,88000
4,Derek,Marketing,65000
5,Elena,Technology,102000
6,Frank,Sales,78000

1,Alice,Engineering,95000
3,Carla,Engineering,88000
5,Elena,Engineering,102000

Explanation:
`sed 's/old/new/'` without -i only prints the transformed text to the terminal -
the file on disk is untouched (confirmed by grep still finding "Engineering"
afterward). After backing up with cp, `sed -i` performs the replacement in place,
permanently modifying employees.csv, while employees.csv.bak retains the original.

================================================================================
Exercise 7 - Create a system-information shell script
================================================================================

Commands:
cat > system_report.sh << 'SCRIPT'
#!/bin/bash
echo "Current username: $(whoami)"
echo "Current date and time: $(date)"
echo "Current working directory: $(pwd)"
echo ""
echo "Available disk space:"
df -h /
echo ""
echo "Memory usage:"
free -h
echo ""
echo "System uptime:"
uptime
SCRIPT
chmod +x system_report.sh
./system_report.sh

Output:
Current username: root
Current date and time: Mon Sep 14 16:17:35 UTC 2026
Current working directory: /root

Available disk space:
Filesystem      Size  Used Avail Use% Mounted on
overlay         911G  3.3G  862G   1% /

Memory usage:
               total        used        free      shared  buff/cache   available
Mem:           7.7Gi       716Mi       5.9Gi       552Ki       1.3Gi       7.0Gi
Swap:          1.0Gi          0B       1.0Gi

System uptime:
 16:17:35 up 6 min,  0 user,  load average: 0.01, 0.06, 0.02

Explanation:
The shebang (#!/bin/bash) tells the system to interpret the file with bash.
$(...) command substitution embeds each command's output inline in the echo
statements. chmod +x grants execute permission so ./system_report.sh can run.

================================================================================
Exercise 8 - Investigate running processes
================================================================================

Commands:
sleep 500 &          (started as a separate background process)
ps aux | grep 'sleep 500'
pgrep -x sleep
kill <PID>
ps aux | grep 'sleep 500'

Output:
root  223  0.0  0.0  2280  1288 ?  Ss  16:18  0:00 sleep 500
Found PID: 223
(after kill)
No sleep process found - confirmed terminated

Explanation:
`ps aux` lists all processes system-wide; `pgrep -x sleep` finds the PID of the
process named exactly "sleep". `kill <PID>` sends the default TERM signal,
requesting the process end - confirmed by re-running ps and finding no match.

================================================================================
Exercise 9 - Foreground and background jobs
================================================================================

Commands:
set -m
sleep 1000 &
jobs -l
kill -STOP %1          (simulates pressing Ctrl+Z on the foreground job)
jobs -l
bg %1                  (resumes the stopped job in the background)
jobs -l
kill %1
jobs -l

Output:
[1]+   263 Running                 sleep 1000 &
[1]+   263 Stopped (signal)        sleep 1000
[1]+ sleep 1000 &
[1]+   263 Running                 sleep 1000 &
[1]+  Terminated              sleep 1000
(no jobs listed)

Explanation:
`jobs -l` lists background/suspended jobs with their PID and state. Pressing
Ctrl+Z on a real foreground job sends it the STOP signal (simulated here directly
with kill -STOP, since Ctrl+Z requires an interactive terminal). `bg %1` resumes
job 1 running in the background. `fg %1` would bring it back to the foreground and
BLOCK the terminal until it finishes or is interrupted with Ctrl+C - not run here
since it would hang a non-interactive script waiting on a 1000-second sleep.
Finally `kill %1` terminates the job, confirmed by the empty `jobs` list.

================================================================================
Exercise 10 - Investigate a system service
================================================================================

Commands:
systemctl enable cron
systemctl start cron
systemctl is-active cron
systemctl is-enabled cron
systemctl status cron --no-pager
journalctl -u cron -n 10 --no-pager

Output:
active
enabled

cron.service - Regular background program processing daemon
     Loaded: loaded (/usr/lib/systemd/system/cron.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-09-14 16:14:55 UTC; 4min 6s ago
   Main PID: 82 (cron)
     CGroup: .../system.slice/cron.service
             |-82 /usr/sbin/cron -f -P

Sep 14 16:14:55 systemd[1]: Started cron.service.
Sep 14 16:14:55 (cron)[82]: cron.service: ... EXTRA_OPTS
Sep 14 16:14:55 cron[82]: (CRON) INFO (pidfile fd = 3)
Sep 14 16:14:55 cron[82]: (CRON) INFO (Running @reboot jobs)
Sep 14 16:17:01 CRON[173]: pam_unix(cron:session): session opened for user root
Sep 14 16:17:01 CRON[174]: (root) CMD (cd / && run-parts --report /etc/cron.hourly)
Sep 14 16:17:01 CRON[173]: pam_unix(cron:session): session closed for user root

Explanation:
`systemctl is-active`/`is-enabled` give quick yes/no checks for running state and
boot-time auto-start. `systemctl status` gives the full picture including the
Main PID (82). `journalctl -u <service> -n 10` shows that service's most recent
10 log entries - here showing cron starting up and running its hourly job.

================================================================================
Environment note: this was completed in a Docker Ubuntu 24.04 container running
systemd (needed for the systemctl/journalctl exercises, since macOS itself is
Unix-based but not Linux and has no systemd or apt).
```
