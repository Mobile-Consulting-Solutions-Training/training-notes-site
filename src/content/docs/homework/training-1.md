---
title: Training 1 Homework
description: Linux Users, Permissions, Text Processing and Processes assignment
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

