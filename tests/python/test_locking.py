import ubelt as ub
import threading


cv = threading.Condition()
updater_lock = threading.RLock()
updater = {}

cache = {}

_NOT_FOUND = ub.NoParam

attrname = 'attr'


def func(this_id, arg):
    import time
    print('arg = {!r}'.format(arg))
    time.sleep(0.001)
    if arg > 0:
        worker(this_id, arg - 1)


def worker(this_id, arg):

    key = this_id
    this_thread = threading.get_ident()

    with updater_lock:
        reentrant = updater.get(key) == this_thread
        wait = updater.setdefault(key, this_thread) != this_thread
        print('this_thread = {!r}'.format(this_thread))
        print('this_id = {!r}'.format(this_id))
        print('updater = {}'.format(ub.repr2(updater, nl=1)))
        print('reentrant = {}'.format(ub.color_text(str(reentrant), "red" if reentrant else "green")))
        print('wait = {}'.format(ub.color_text(str(wait), "red" if wait else "green")))

    if wait:
        with cv:
            while key in updater:
                cv.wait()
            print('updater = {}'.format(ub.repr2(updater, nl=1)))

    val = cache.get(attrname, _NOT_FOUND)
    if val is not _NOT_FOUND:
        if not reentrant:
            with updater_lock:
                updater.pop(key, None)
            with cv:
                cv.notify_all()
    else:
        # Call the underlying function to compute the value.
        try:
            val = func(this_id, arg)
        except Exception:
            with updater_lock:
                updater.pop(key, None)
            with cv:
                cv.notify_all()
            raise

        # Attempt to store the value
        try:
            cache[attrname] = val
        except TypeError:
            with updater_lock:
                updater.pop(key, None)
            with cv:
                cv.notify_all()
            msg = (
                f"The '__dict__' attribute on {type(this_id).__name__!r} instance "
                f"does not support item assignment for caching {attrname!r} property."
            )
            raise TypeError(msg) from None

        # Value has been computed and cached.  Now return it.
        if not reentrant:
            with updater_lock:
                updater.pop(key, None)
            with cv:
                cv.notify_all()
    return val


def main():
    pool = ub.JobPool('thread', max_workers=10)

    for i in range(100000):
        pool.submit(worker, i % 10, 3)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_locking.py
    """
    main()
