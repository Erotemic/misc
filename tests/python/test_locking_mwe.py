import ubelt as ub
import random
import threading
import time

cv = threading.Condition()
updater_lock = threading.RLock()
updater = {}
cache = {}
_NOT_FOUND = object()
attrname = 'attr'


WITH_FIX = 0   # set to zero to cause deadlocks
DEBUG_PRINTS = 0


class ThreadUnsafe():

    def __init__(self):
        self.lock1 = threading.Lock()
        self.lock2 = threading.Lock()
        pass

    def __call__(self):
        """
        This function has a high probability of deadlock if it runs simultaniously
        with another version of itself.
        """
        thread_id = threading.get_ident()
        this_id = id(self)
        if DEBUG_PRINTS:
            if random.random() > 0.5:
                print('[{}.{}.v1] aquire outer lock1'.format(thread_id, this_id))
                with self.lock1:
                    print('[{}.{}.v1] aquired outer lock1'.format(thread_id, this_id))
                    print('[{}.{}.v1] aquire inner lock2'.format(thread_id, this_id))
                    with self.lock2:
                        print('[{}.{}.v1] aquired inner lock2'.format(thread_id, this_id))
                        print('[{}.{}.v1] releasing inner lock2'.format(thread_id, this_id))
                    print('[{}.{}.v1] released  inner lock2'.format(thread_id, this_id))
                    print('[{}.{}.v1] releasing  outer lock1'.format(thread_id, this_id))
                print('[{}.{}.v1] released  outer lock1'.format(thread_id, this_id))
            else:
                print('[{}.{}.v2] aquire outer lock2'.format(thread_id, this_id))
                with self.lock2:
                    print('[{}.{}.v2] aquired outer lock2'.format(thread_id, this_id))
                    print('[{}.{}.v2] aquire inner  lock1'.format(thread_id, this_id))
                    with self.lock1:
                        print('[{}.{}.v2] aquired   inner lock1'.format(thread_id, this_id))
                        print('[{}.{}.v2] releasing inner lock1'.format(thread_id, this_id))
                    print('[{}.{}.v2] released  inner lock1'.format(thread_id, this_id))
                    print('[{}.{}.v2] releasing  outer lock2'.format(thread_id, this_id))
                print('[{}.{}.v2] released  outer lock2'.format(thread_id, this_id))
        else:
            if random.random() > 0.5:
                with self.lock1:
                    time.sleep(0.03)
                    with self.lock2:
                        ...
            else:
                with self.lock2:
                    time.sleep(0.03)
                    with self.lock1:
                        ...

unsafe_instances = {
    i: ThreadUnsafe() for i in range(3)
}


def func(this_id):
    unsafe_instances[this_id]()


def worker(this_id):
    key = this_id
    this_thread = threading.get_ident()

    reentrant = 0
    wait = 0

    with updater_lock:
        reentrant = updater.get(key) == this_thread
        wait = updater.setdefault(key, this_thread) != this_thread

    if WITH_FIX:
        while wait:
            with cv:
                while this_thread != updater.get(key, this_thread):
                    cv.wait()
                with updater_lock:
                    reentrant = updater.get(key) == this_thread
                    wait = updater.setdefault(key, this_thread) != this_thread
    else:
        if wait:
            with cv:
                with updater_lock:
                    reentrant = updater.get(key) == this_thread
                    wait = updater.setdefault(key, this_thread) != this_thread

    ####

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
            val = func(this_id)
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
    pool = ub.JobPool('thread', max_workers=4)

    for i in range(20):
        random_ids = [random.randint(0, 1) for _ in range(1000)]

        for this_id in random_ids:
            pool.submit(worker, this_id)

        finished_jobs = [job for job in ub.ProgIter(pool.as_completed(), total=len(pool))]
        for job in finished_jobs:
            try:
                job.result()
            except Exception as ex:
                print('ex = {!r}'.format(ex))
                pass


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_locking_mwe.py
    """
    main()
