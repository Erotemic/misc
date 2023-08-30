Oh Sadness
==========

PSA: Last night there was a power outage and my machine hard shut down while I
was working on it  After the power came on I tried to boot the machine and was
treated to my first experience where an unsafe shutdown caused an error.

The boot sequence got stuck on:

```
Failed to start default target: Transaction for graphics.target/start is destructive (emergency.target has 'start' job queued, but 'stop' is included in this transaction).
```

Rebooting resulted in the same message.

Fortunately the error was googleable. I found information that pointed me to
the `fsck` command, which is sometimes able to fix corrupted filesystems.

In addition to this I also had to edit my `/etc/fstab` because for whatever
reason my machine switched the names it assigned to the disks. This is a lesson
that it's a good idea to use the `/dev/disk/by-id/...` name rather than the
`/dev/...` name.


Details
=======


On 2023-08-06 there was a power outage, which caused a hard shutdown on my machine I was working on.

FOr more details, the message was:

.. code::

    a start job is running for /dev/nvme0n1p1
    [TIME] Timed out waiting for device /dev/nvme0n1p1
    [DEPEND] Dependency failed for File System Check on /devnvme0n1p1
    [DEPEND] Dependency failed for /boot/efi
    [DEPEND] Dependency failed for Local File Systems
    [OK] Stopped Dispatch Password Requestes to Cosole Directory Watch
    [OK] Started Emergency Shell Dispatch Password Requestes to Cosole Directory Watch
    [OK] Reached target Emergency Mode
    [OK] Reached target System Initialization
    [OK] Started ntp-systemd-netif.service

    You are in emergeny mode. After logging in, type "journalctl -xb" to view system logs, "systemctl reboot" to reboot, "systemctl default" or "exit" to boot into default mode.
    Press Enter for maintenance
    or press Control-D to continue.

On this I press enter, and try to muck with things. At one point exiting this
brought me into a loop where I had to exit a lot of emergency prompts. But
usually it ends with this.


.. code::

   Failed to start default target: Transaction for graphics.target/start is destructive (emergency.target has 'start' job queued, but 'stop' is included in this transaction).


When I try to type ``systemctl reboot`` I get:

.. code::

   Failed to connect to bus: No suchfile or directory.
   Failed to start reboot.target target: Transaction for reboot.target/start is destructive (emergency.target has 'start' job queued, but 'stop' is included in this transaction).
   See system logs and 'systemctl status reboot.target' for details

In the system logs with ``journalctl -xb`` I see:

/dev/nvme1n1: cant't open blockdev (but that was for an older command?)

Newer related stuff was

.. code::

    systemd[1] sysinit.target: Found ordering cycle on grub-initrd-fallback.service/stpo
    systemd[1] sysinit.target: Found dependency on emergency.target/stop
    systemd[1] sysinit.target: Found dependency on sysinit.target/stop
    systemd[1] sysinit.target: Job grub-initrd-fallback.service/stop deleted to break ordering cycle starting with sysinit.target/stop
    Requested transaction contradicts existing jobs: Transaction for reboot.target/start is destructive .. yadaydada


Disks By ID
===========

/dev/disk/by-id/nvme-Sabrent_Rocket_4.0_1TB_038070918D88300410 - LVM managed with ext4 boot drive
/dev/disk/by-id/nvme-Samsung_SSD_970_EVO_Plus_2TB_S9CNM0RB05028D - btrfs data
/dev/disk/by-id/nvme-Samsung_SSD_970_EVO_Plus_2TB_S9CNM0RB05113H - zfs L2 ARC


Debugging Steps
===============

For my btrfs data drive, I changed fstab which was pointing at /dev/nvme1n1
to point at /dev/disk/by-id/nvme-Samsung_SSD_970_EVO_Plus_2TB_S9CNM0RB05028D
I also commented it out to make things simpler. Will reenable later.

Also switched the /boot/efi drive from the /dev/nvme0n1p1 to its by-id variant
which is the sabrenet rocket with a -part1 suffix.


Resolution
==========

After yet another reboot, it seemed to work.
I think it was a combination of bootint into a live disk and running fsck on the disk with my primary partition (I think the oot section was weird?) and then updating /etc/fstab to use device ids instead of the raw paths (which seemed to have changedfor whatever reason)


References
==========

https://askubuntu.com/questions/1319227/transaction-for-graphical-target-start-is-destructive

https://forums.linuxmint.com/viewtopic.php?t=366146
