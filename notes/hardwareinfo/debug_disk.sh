#!/usr/bin/env bash
__doc__="

How to read smartctl output:

    https://en.wikipedia.org/wiki/S.M.A.R.T.#Known_ATA_S.M.A.R.T._attributes

References:
    https://superuser.com/questions/1315167/zfs-scrub-finds-checksum-errors-but-badblocks-and-smartctl-do-not
    https://unix.stackexchange.com/questions/61818/smartctl-retest-bad-sectors
    https://wiki.archlinux.org/title/badblocks
    https://superuser.com/questions/1315167/zfs-scrub-finds-checksum-errors-but-badblocks-and-smartctl-do-not
    https://www.reddit.com/r/zfs/comments/kcqmp0/too_many_read_and_checksum_errors_but_smart_tests/
"

sudo smartctl --all /dev/sda
sudo smartctl --all /dev/sdb
sudo smartctl --all /dev/sdc
sudo smartctl --all /dev/sdd
sudo smartctl --all /dev/sde

sudo smartctl --all /dev/nvme0n1


sudo smartctl -t short /dev/sda
sudo smartctl -t short /dev/sdb
sudo smartctl -t short /dev/sdc
sudo smartctl -t short /dev/sdd


#Issue 2022-08-28
#        NAME                                                 STATE     READ WRITE CKSUM
#        data                                                 DEGRADED     0     0     0
#          mirror-0                                           DEGRADED     0     0     0
#            wwn-0x5000c5009399acab                           DEGRADED    89     0   245  too many errors  (repairing)
#            wwn-0x5000c500a4d78d92                           ONLINE       0     0     0


# https://unix.stackexchange.com/questions/61818/smartctl-retest-bad-sectors


#[102757.667209] ata3.00: configured for UDMA/133
#[102757.667242] sd 2:0:0:0: [sda] tag#5 FAILED Result: hostbyte=DID_OK driverbyte=DRIVER_OK cmd_age=0s
#[102757.667249] sd 2:0:0:0: [sda] tag#5 Sense Key : Illegal Request [current]
#[102757.667254] sd 2:0:0:0: [sda] tag#5 Add. Sense: Unaligned write command
#[102757.667259] sd 2:0:0:0: [sda] tag#5 CDB: Read(16) 88 00 00 00 00 04 0a 18 92 38 00 00 01 00 00 00
#[102757.667262] blk_update_request: I/O error, dev sda, sector 17349251640 op 0x0:(READ) flags 0x700 phys_seg 2 prio class 0
#[102757.667279] zio pool=data vdev=/dev/disk/by-id/wwn-0x5000c5009399acab-part1 error=5 type=1 offset=8882815791104 size=131072 flags=1808b0
#[102757.667310] sd 2:0:0:0: [sda] tag#9 FAILED Result: hostbyte=DID_OK driverbyte=DRIVER_OK cmd_age=0s
#[102757.667313] sd 2:0:0:0: [sda] tag#9 Sense Key : Illegal Request [current]
#[102757.667318] sd 2:0:0:0: [sda] tag#9 Add. Sense: Unaligned write command
#[102757.667321] sd 2:0:0:0: [sda] tag#9 CDB: Read(16) 88 00 00 00 00 04 0a 18 82 38 00 00 08 00 00 00
#[102757.667324] blk_update_request: I/O error, dev sda, sector 17349247544 op 0x0:(READ) flags 0x700 phys_seg 16 prio class 0
#[102757.667334] zio pool=data vdev=/dev/disk/by-id/wwn-0x5000c5009399acab-part1 error=5 type=1 offset=8882813693952 size=1048576 flags=40080cb0
#[102757.667352] sd 2:0:0:0: [sda] tag#30 FAILED Result: hostbyte=DID_OK driverbyte=DRIVER_OK cmd_age=0s
#[102757.667356] sd 2:0:0:0: [sda] tag#30 Sense Key : Illegal Request [current]
#[102757.667360] sd 2:0:0:0: [sda] tag#30 Add. Sense: Unaligned write command
#[102757.667363] sd 2:0:0:0: [sda] tag#30 CDB: Read(16) 88 00 00 00 00 04 0a 18 8a 38 00 00 08 00 00 00
#[102757.667366] blk_update_request: I/O error, dev sda, sector 17349249592 op 0x0:(READ) flags 0x700 phys_seg 16 prio class 0
#[102757.667372] zio pool=data vdev=/dev/disk/by-id/wwn-0x5000c5009399acab-part1 error=5 type=1 offset=8882814742528 size=1048576 flags=40080cb0
#[102757.667383] ata3: EH complete


sudo hdparm --read-sector 17349251640 /dev/sda
sudo hdparm --read-sector 17349247544 /dev/sda
sudo hdparm --read-sector 17349249592 /dev/sda1

sudo smartctl -t long /dev/sda


run_badblocks_online(){
    __doc__="
    Runs badblocks on a device with options for it in non-destructive mode.
    "
    DEV=/dev/sda
    # Parse out the correct blocksize for the disk in question.
    BLOCK_SIZE=$(lsblk -o NAME,PHY-SeC,type $DEV --json | jq -r '.blockdevices[0]["phy-sec"]')
    echo "BLOCK_SIZE = $BLOCK_SIZE"
    BLOCKS_PER_TEST=1024
    #sudo badblocks -nsv -b "$BLOCK_SIZE" -c "$BLOCKS_PER_TEST" "$DEV"
    sudo badblocks -sv -b "$BLOCK_SIZE" -c "$BLOCKS_PER_TEST" "$DEV"
}


lsblk

_='
    GOT:

        2021-07-09 19:49:14,771 ERROR: unexpected error - [Errno 5] Input/output error
          File "/home/joncrall/.pyenv/versions/3.8.5/envs/pyenv3.8.5/lib/python3.8/site-packages/dvc/utils/__init__.py", line 30, in _fobj_md5
            data = fobj.read(LOCAL_CHUNK_SIZE)
        OSError: [Errno 5] Input/output error


        2021-07-09 20:43:06,952 DEBUG: state save (3878886, 1625846781937921024, 136774) fcf07108afd230026045cf20861740f1
        2021-07-09 20:43:06,954 TRACE: cache "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/fc/f07108afd230026045cf20861740f1" expected "md5: fcf07108afd230026045cf20861740f1" actual "md5: fcf07108afd230026045cf20861740f1"
        2021-07-09 20:43:06,957 TRACE: Path "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/5d/c2319f95b0536119060eb1c2fc875d" inode "3884336"
        2021-07-09 20:43:06,962 TRACE: Path "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/5d/c2319f95b0536119060eb1c2fc875d" inode "3884336"
        2021-07-09 20:43:06,963 DEBUG: state save (3884336, 1625847850297639936, 428) 5dc2319f95b0536119060eb1c2fc875d
        2021-07-09 20:43:06,964 TRACE: cache "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/5d/c2319f95b0536119060eb1c2fc875d" expected "md5: 5dc2319f95b0536119060eb1c2fc875d" actual "md5: 5dc2319f95b0536119060eb1c2fc875d"
        2021-07-09 20:43:06,966 TRACE: Path "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/7c/a92f4b09c3141e8f2dd25983a3aecc" inode "3881181"
        2021-07-09 20:43:07,163 ERROR: unexpected error - [Errno 5] Input/output error
        ------------------------------------------------------------
        Traceback (most recent call last):
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/main.py", line 55, in main
            ret = cmd.do_run()
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/command/base.py", line 50, in do_run
            return self.run()
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/command/data_sync.py", line 30, in run
            stats = self.repo.pull(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/repo/__init__.py", line 51, in wrapper
            return f(repo, *args, **kwargs)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/repo/pull.py", line 29, in pull
            processed_files_count = self.fetch(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/repo/__init__.py", line 51, in wrapper
            return f(repo, *args, **kwargs)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/repo/fetch.py", line 70, in fetch
            d, f = _fetch_naive_objs(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/repo/fetch.py", line 110, in _fetch_naive_objs
            downloaded += repo.cloud.pull(objs, **kwargs)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/data_cloud.py", line 105, in pull
            return remote_obj.pull(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/remote/base.py", line 57, in wrapper
            return f(obj, *args, **kwargs)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/remote/base.py", line 517, in pull
            ret = self._process(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/remote/base.py", line 351, in _process
            dir_status, file_status, dir_contents = self._status(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/remote/base.py", line 178, in _status
            cache.hashes_exist(md5s, jobs=jobs, name=cache.cache_dir)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/objects/db/local.py", line 76, in hashes_exist
            self.check(hash_info)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/objects/db/base.py", line 152, in check
            obj.check(self, check_hash=check_hash)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/objects/file.py", line 71, in check
            actual = get_file_hash(
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/objects/stage.py", line 53, in get_file_hash
            hash_info = _get_file_hash(path_info, fs, name)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/objects/stage.py", line 39, in _get_file_hash
            name, file_md5(path_info, fs), size=fs.getsize(path_info)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/utils/__init__.py", line 69, in file_md5
            _fobj_md5(fobj, hash_md5, binary, pbar.update)
          File "/home/joncrall/.pyenv/versions/3.8.6/envs/pyenv3.8.6/lib/python3.8/site-packages/dvc/utils/__init__.py", line 30, in _fobj_md5
            data = fobj.read(LOCAL_CHUNK_SIZE)
        OSError: [Errno 5] Input/output error
        ------------------------------------------------------------
        2021-07-09 20:43:07,300 DEBUG: Version info for developers:
        DVC version: 2.5.4 (pip)
        ---------------------------------
        Platform: Python 3.8.6 on Linux-5.11.0-22-generic-x86_64-with-glibc2.2.5
        Supports:
            http (requests = 2.25.1),
            https (requests = 2.25.1),
            s3 (s3fs = 2021.6.1, boto3 = 1.17.49),
            ssh (paramiko = 2.7.2)
        Cache types: hardlink, symlink
        Cache directory: zfs on data
        Caches: local
        Remotes: ssh, ssh, s3
        Workspace directory: zfs on data
        Repo: dvc, git

        Having any troubles? Hit us up at https://dvc.org/support, we are always happy to help!
        2021-07-09 20:43:07,304 DEBUG: Analytics is enabled.
        2021-07-09 20:43:07,345 DEBUG: Trying to spawn "["daemon", "-q", "analytics", "/tmp/tmp7amlafj3"]"
        2021-07-09 20:43:07,346 DEBUG: Spawned "["daemon", "-q", "analytics", "/tmp/tmp7amlafj3"]"


        (pyenv3.8.6) joncrall@toothbrush:~/data/dvc-repos/dvc_project/drop1$ md5sum /data/joncrall/dvc-repos/dvc_project/.dvc/cache/7c/a92f4b09c3141e8f2dd25983a3aecc
        md5sum: /data/joncrall/dvc-repos/dvc_project/.dvc/cache/7c/a92f4b09c3141e8f2dd25983a3aecc: Input/output error


        I then rmed the file

        But got a new one


        2021-07-09 20:46:47,371 TRACE: Assuming "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/1d/bf39985b1e60ee4d7ec4808413cc20" is unchanged since it is read-only
        2021-07-09 20:46:47,372 TRACE: Path "/data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/086220831c8db4a2085fa2d0aa5a54" inode "3883745"
        2021-07-09 20:46:47,938 ERROR: unexpected error - [Errno 5] Input/output error
        ------------------------------------------------------------

        (pyenv3.8.6) joncrall@toothbrush:~/data/dvc-repos/dvc_project/drop1$ sha1sum /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/086220831c8db4a2085fa2d0aa5a54
        sha1sum: /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/086220831c8db4a2085fa2d0aa5a54: Input/output error


        # hangs
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/0*

        # does not hang
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/1*

        # hangs (but not anymore)
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/2*

        # does not hang
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/3*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/4*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/5*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/6*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/7*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/8*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/9*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/a*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/b*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/c*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/d*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/e*
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/f*

        # but doesnt hang?
        strace ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/

        # works
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/1*

        # works
        ls /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/086220831c8db4a2085fa2d0aa5a54

        # works
        (pyenv3.8.6) joncrall@toothbrush:/data/joncrall/dvc-repos/dvc_project/.dvc/cache$ sha1sum /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/1a0fc907692b856aa6c61780b77d57
        873aa3a6b4654ae685e4d798152399b4b6b44b02  /data/joncrall/dvc-repos/dvc_project/.dvc/cache/8a/1a0fc907692b856aa6c61780b77d57


'
