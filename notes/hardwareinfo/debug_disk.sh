sudo smartctl --all /dev/sda 
sudo smartctl --all /dev/sdb
sudo smartctl --all /dev/sdc 
sudo smartctl --all /dev/sdd

sudo smartctl --all /dev/nvme0n1

lsblk

'


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
