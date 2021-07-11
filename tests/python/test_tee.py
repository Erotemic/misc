from __future__ import unicode_literals

import atexit
import errno
import multiprocessing
import io
import os
import re
import select
import sys
import ctypes
import traceback
import signal
import tempfile
import subprocess
import threading
import queue
from threading import Thread
from contextlib import contextmanager

from typing import Optional  # novm
from types import ModuleType  # novm

import ctypes
import io
import os
import sys
import tempfile


def test_redirect():
    """
    python ~/misc/tests/python/test_tee.py
    """
    # sys_attr = 'stdout'
    # redirector = PosixRedictSystemStream(sys_attr)
    # with redirector:
    #     import ubelt as ub
    #     cmake_exe = ub.find_exe('cmake')
    #     subprocess.run([cmake_exe, '--version'])
    #     print('hello world')
    # redirector.logfile.seek(0)
    # captured = redirector.logfile.read()
    # print('captured = {!r}'.format(captured))
    # print('---------')

    import tempfile
    import ubelt as ub
    from os.path import join
    dpath = tempfile.mkdtemp()
    # This should probably be the real log file. But it must live on disk!
    fpath = join(dpath, 'stream_queue')
    writer = open(fpath, mode='wb+')
    reader = open(fpath, mode='rb+')

    sys_attr = 'stdout'
    redirector = PosixRedictSystemStream(sys_attr, writer)

    echo_writer = open(os.dup(sys.stdout.fileno()), "w")

    from threading import Thread

    _kill = threading.Event()
    def background_reader(reader, echo_writer, redirector, _kill):
        while True:
            is_killed = _kill.wait(.1)
            if is_killed:
                break
            redirector.flush()
            line = reader.readline()
            while line:
                echo_writer.write('thread write: {}\n'.format(line))
                line = reader.readline()

    cmake_exe = ub.find_exe('cmake')
    with redirector:

        _thread = Thread(target=background_reader, args=(reader, echo_writer, redirector, _kill))
        _thread.daemon = True  # thread dies with the program
        _thread.start()

        print('hello world')

        subprocess.run([cmake_exe, '--version'])

        subprocess.run([cmake_exe, '--version'])
        print('hello world')
    _kill.set()

    print('finished redirection')
    print('finished redirection')


class PosixRedictSystemStream:
    """
    References:
        https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/

    Example:
        >>> sys_attr = 'stdout'
        >>> redirector = PosixRedictSystemStream(sys_attr)
        >>> with redirector:
        >>>     import ubelt as ub
        >>>     cmake_exe = ub.find_exe('cmake')
        >>>     subprocess.run([cmake_exe, '--version'])
        >>>     print('hello world')
        >>> print('redirector.captured = {!r}'.format(redirector.captured))
    """
    def __init__(self, sys_attr, logfile=None):
        self.sys_attr = sys_attr
        self.libc = None
        self.c_stream = None
        self.sys_stream = None
        self.orig_stream_fd = None
        if logfile is None:
            self.logfile = tempfile.TemporaryFile(mode='w+b')
        else:
            self.logfile = logfile
        self.saved_sys_stream_fd = None

    def __enter__(self):
        # The original fd stdout points to. Usually 1 on POSIX systems for stdout.
        self.libc = ctypes.CDLL(None)

        self.c_stream = ctypes.c_void_p.in_dll(self.libc, self.sys_attr)

        sys_stream = getattr(sys, self.sys_attr)
        self.orig_sys_stream_fd = sys_stream.fileno()

        # Save a copy of the original stdout fd in saved_sys_stream_fd
        self.saved_sys_stream_fd = os.dup(self.orig_sys_stream_fd)

        # Create a temporary file and redirect stdout to it
        self._redirect_orig_stream(self.logfile.fileno())

    def __exit__(self, a, b, c):
        try:
            # then redirect stdout back to the saved fd
            if self.saved_sys_stream_fd is not None:
                self._redirect_orig_stream(self.saved_sys_stream_fd)
        finally:
            if self.saved_sys_stream_fd is not None:
                os.close(self.saved_sys_stream_fd)

    def _redirect_orig_stream(self, to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        self.libc.fflush(self.c_stream)
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys_stream = getattr(sys, self.sys_attr)
        sys_stream.flush()
        sys_stream.close()
        # Make orig_sys_stream_fd point to the same file as to_fd
        os.dup2(to_fd, self.orig_sys_stream_fd)
        # Set sys.stdout to a new stream that points to the redirected fd
        new_buffer = open(self.orig_sys_stream_fd, 'wb')
        new_stream = io.TextIOWrapper(new_buffer)
        setattr(sys, self.sys_attr, new_stream)
        self.sys_stream = getattr(sys, self.sys_attr)

    def flush(self):
        self.libc.fflush(self.c_stream)
        self.sys_stream.flush()


class winlog:
    def __init__(self, filen, echo=True, debug=0):
        print("winlog.__init__")
        self.filen = filen
        self.echo = echo
        self.debug = debug
        self._active = False  # used to prevent re-entry

    def __enter__(self):
        print("winlog.__enter__")
        if self._active:
            raise RuntimeError("Can't re-enter the same log_output!")
        if self.filen is None:
            raise RuntimeError(
                "file argument must be set by either __init__ or __call__")
        self.saved_stdout = sys.stdout.fileno()
        self.new_stdout = os.dup(self.saved_stdout)
        self.saved_stderr = sys.stderr.fileno()
        self.new_stderr = os.dup(self.saved_stderr)

        self._kill = threading.Event()
        print("winlog.__enter__ [about to start thread]")
        _thread = Thread(
            target=self.tee_output, args=(
                self.new_stdout, self.new_stderr))
        _thread.daemon = True
        _thread.start()
        print("winlog.__enter__ [thread has been started]")
        self.active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("winlog.__exit__")
        self._kill.set()
        self.active = False

    def _textio_iterlines(self, stream):
        line = stream.readline()
        while line != '':
            yield line
            line = stream.readline()

    def tee_output(self, stdout_fd, stderr_fd):
        # ignore stderr until we figure out how to read a line
        print("winlog.tee_output")

        with open(stdout_fd, 'w+') as stream_out:
            with open(self.filen, "w") as log_file:
                while True:
                    print('before readline')
                    line = stream_out.readline()
                    if self.echo:
                        stream_out.write(line)
                    log_file.write(line)
                    is_killed = self._kill.wait(.1)
                    if is_killed:
                        break


def testme():
    import ubelt as ub
    cmake_exe = ub.find_exe('cmake')
    print('cmake_exe = {!r}'.format(cmake_exe))
    fpath = "build-out.txt"
    echo = False
    with winlog(fpath, echo) as logger:  # NOQA
        print("INSIDE LOGGER")
        # p = subprocess.run("c:/Program Files/CMake/bin/cmake --version")
        p = subprocess.run("{} --version".format(cmake_exe), shell=True)  # NOQA

    import ubelt as ub
    cmake_exe = ub.find_exe('cmake')
    with ub.CaptureStdout() as cap:
        p = subprocess.run([cmake_exe, '--version'])


if __name__ == '__main__':
    # testme()
    test_redirect()
