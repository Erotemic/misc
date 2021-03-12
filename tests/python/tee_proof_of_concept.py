import ctypes
import io
import os
import subprocess
import tempfile
import threading
from os.path import sys


def main():
    import ubelt as ub

    # This should probably be the real log file. But it must live on disk!
    # from os.path import join
    # dpath = tempfile.mkdtemp()
    # fpath = join(dpath, 'stream_queue')
    # writer = open(fpath, mode='wb+')
    # reader = open(fpath, mode='rb+')

    fpath = 'a-test-log-file.txt'
    writer = open(fpath, mode='wb+')
    writer.write(b'')
    reader = open(fpath, mode='rb+')

    sys_attr = 'stdout'
    redirector = RedirectSystemStream(sys_attr, writer)

    echo_writer = open(os.dup(sys.stdout.fileno()), "w")

    from threading import Thread

    logged_lines = []

    _kill = threading.Event()
    def background_reader(reader, echo_writer, redirector, _kill):
        while True:
            is_killed = _kill.wait(.1)
            # echo_writer.write('check\n')
            redirector.flush()
            line = reader.readline()
            while line:
                logged_lines.append(line)
                echo_writer.write('thread write: {}\n'.format(line))
                echo_writer.flush()
                line = reader.readline()

            # echo_writer.write('check is_killed={}\n'.format(is_killed))
            if is_killed:
                break

    cmake_exe = ub.find_exe('cmake')
    with redirector:

        _thread = Thread(target=background_reader, args=(reader, echo_writer, redirector, _kill))
        # _thread.daemon = True  # thread dies with the program
        _thread.start()

        print('hello world')

        subprocess.run([cmake_exe, '--version'])

        subprocess.run([cmake_exe, '--version'])
        print('hello world')

        redirector.flush()
        # import time
        # time.sleep(0.1)
        _kill.set()
        _thread.join()

    echo_writer.flush()
    print('logged_lines = {!r}'.format(logged_lines))

    print('finished redirection')
    print('finished redirection')


class RedirectSystemStream:
    """
    References:
        https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/

    Example:
        >>> sys_attr = 'stdout'
        >>> redirector = RedirectSystemStream(sys_attr)
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

        if sys.platform.startswith('win32'):
            ### ALL THIS IS NEW ########################################
            if sys.version_info < (3, 5):
                libc = ctypes.CDLL(ctypes.util.find_library('c'))
            else:
                if hasattr(sys, 'gettotalrefcount'):  # debug build
                    libc = ctypes.CDLL('ucrtbased')
                else:
                    libc = ctypes.CDLL('api-ms-win-crt-stdio-l1-1-0')

            # c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
            kernel32 = ctypes.WinDLL('kernel32')

            # https://docs.microsoft.com/en-us/windows/console/getstdhandle
            if self.sys_attr == 'stdout':
                STD_HANDLE = -11
            elif self.sys_attr == 'stderr':
                STD_HANDLE = -12
            else:
                raise KeyError(self.sys_attr)

            c_stdout = kernel32.GetStdHandle(STD_HANDLE)

            self.libc = libc
            self.c_stream = c_stdout
            ##############################################################
        else:
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
        if sys.platform.startswith('win32'):
            self.libc.fflush(None)
        else:
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
        if sys.platform.startswith('win32'):
            self.libc.fflush(None)
        else:
            self.libc.fflush(self.c_stream)
        self.sys_stream.flush()

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/tee_proof_of_concept.py
    """
    main()
