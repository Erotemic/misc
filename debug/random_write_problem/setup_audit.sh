#!/bin/bash
__doc__="
We are going to attempt to setup an auditing system to figure out what is
writing these random files.

THe program 'audit' uses a Linux Kernel Integration

References:
    https://chatgpt.com/c/674e2441-680c-8002-9542-58850b949078
    https://sematext.com/glossary/auditd/
    https://goteleport.com/blog/linux-audit/
    https://github.com/ipython/ipython/issues/14812

SeeAlso:
    ~/misc/debug/random_write_problem/seach_audit.py
"

# Install auditd
sudo apt install auditd -y

# Enable the audit deamon
sudo systemctl start auditd
sudo systemctl enable auditd

# Check the status
sudo systemctl status auditd

# List current rules (initially there will be none)
sudo auditctl -l


# Add a rule that watches the home directory
# Note: rules are temporary and will be removed on reboot
# sudo auditctl -w "$HOME" -p rwxa -k home_watch
#-p rwxa: Indicates the types of access to monitor:
# r: Read.
# w: Write.
# x: Execute.
# a: Attribute changes (e.g., ownership or permissions).
sudo auditctl -w "$HOME/code" -p wa -k code_repos_watch
sudo auditctl -w "$HOME/local" -p wa -k local_repo_watch
sudo auditctl -w "$HOME/misc" -p wa -k misc_repo_watch

# List current rules
sudo auditctl -l

# Setup a rule to monitor execve, which will track the execution of new processes along with their pid and ppid.
sudo auditctl -a always,exit -F arch=b64 -S execve -k process_exec
sudo auditctl -a always,exit -F arch=b32 -S execve -k process_exec

# Add persistant rules in this file if desired
sudo cat /etc/audit/rules.d/audit.rules

# Append current rules to persistant rules
sudo sh -c "echo \"$(sudo auditctl -l)\" >> /etc/audit/rules.d/audit.rules"


# Modify the audit configuration to increase the amount of logs kept
tudo cat /etc/audit/auditd.conf

sudo systemctl status auditd
sudo systemctl restart auditd

sudo apt install augeas-tools -y

sudo augtool -A

# Modify autitd config with augtool commands
CONFIG_FILE="/etc/audit/auditd.conf"
COMMANDS="
    # Modify values of a key inside a config file.
    # Maximim size of log files in megabytes
    set /files${CONFIG_FILE}/max_log_file 16
    # Maximim number of log files
    set /files${CONFIG_FILE}/num_logs 999
    # This is just for reporting. It is not necessary.
    print /files${CONFIG_FILE}
"
# Write the modified config to a new file with the ".augnew" extension
echo "Previewing changes to ${CONFIG_FILE}:"
echo "$COMMANDS" | sudo augtool --autosave --new
echo ""
# View the changes
sudo colordiff -u "${CONFIG_FILE}" "${CONFIG_FILE}.augnew"
# Apply the changes
echo "$COMMANDS" | sudo augtool --autosave

# Restart after a config change
sudo systemctl restart auditd

# Generate a report
sudo aureport

# Check for activity
sudo ausearch -k misc_repo_watch -i
sudo ausearch -k local_repo_watch -i
sudo ausearch -k code_repos_watch -i
sudo ausearch -m syscall -i
sudo ausearch -m PATH -i


# Format the date in the current locale for ausearch
START_TIME="$(date -d '2025-03-01' '+%x')"
END_TIME="$(date -d '2025-03-03' '+%x')"
sudo ausearch --start "$START_TIME" --end "$END_TIME"

START_TIME="$(date -d '2025-01-01' '+%x')"
END_TIME="$(date -d '2025-01-03' '+%x')"
sudo ausearch --start "$START_TIME" --end "$END_TIME"

sudo ausearch -k misc_repo_watch -i | grep pandas
sudo ausearch -k local_repo_watch -i | grep pandas
sudo ausearch -k code_repos_watch -i | grep pandas
sudo ausearch -k code_repos_watch -i | grep "erotemic.kwutil"
sudo ausearch -k misc_repo_watch -i | grep poc

sudo ausearch -k code_repos_watch -i | grep .reset_index


# Monitor all process relationships
sudo apt install acct
sudo accton /var/log/pacct
lastcomm

# Enable process accounting
sudo accton on

# To disable process accounting
sudo accton off

lastcomm "$USER"
