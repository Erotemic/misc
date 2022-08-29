"""
Really nice article about how the TTY works:
    http://www.linusakesson.net/programming/tty/

Also good: an answer about how tmux works:
    https://www.quora.com/How-do-I-understand-the-tmux-design-architecture-and-internals

"""
import signal


for sig in signal.valid_signals():
    if hasattr(sig, 'name'):
        print(f'valid enumitem signal {sig.name} {sig.value}')
    else:
        print(f'valid numeric signal {sig}')

for sig in list(signal.Signals):
    print(f'{sig.name} {sig.value}')


def force_segfault():
    import ctypes
    ctypes.string_at(0)
