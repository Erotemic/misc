import ubelt as ub
import random
import time  # NOQA
import threading


cv = threading.Condition()
updater_lock = threading.RLock()
updater = {}

cache = {}

_NOT_FOUND = ub.NoParam

attrname = 'attr'


# https://stackoverflow.com/questions/14288039/simulating-a-deadlock-on-a-thread

account_locks = {
    i: (threading.Lock(), threading.Lock()) for i in range(3)
}

# @ub.memoize
# def account_locks(this_id):
#     accountone = threading.Lock()
#     accounttwo = threading.Lock()
#     return accountone, accounttwo


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

unsafe_instances = {
    i: ThreadUnsafe() for i in range(3)
}


def transfer(accountone, accounttwo):
    accountone.acquire()
    accounttwo.acquire()
    accountone.release()
    accounttwo.release()


def transfer_do(this_id):
    accountone, accounttwo = account_locks[this_id]
    print('this_id = {!r}'.format(this_id))
    for i in range(100):
        transfer(accountone, accounttwo)  # send money from first account to second
        transfer(accounttwo, accountone)  # send money from second account to first


def func(this_id, arg):
    # print('arg = {!r}'.format(arg))
    # time.sleep(0.001)

    # if random.random() > 0.5:
    #     raise Exception

    # if random.random() > 0.5:
    #     cache.clear()

    unsafe_instances[this_id]()

    # transfer_do(this_id)

    # if arg > 0:
    #     return worker(this_id, arg - 1)
    # else:
    #     return this_id


def classic():
    for x in range(300):
        this_id = 1
        t = threading.Thread(target=transfer_do, args=(this_id,))
        t.start()


def worker(this_id, arg):
    key = this_id
    this_thread = threading.get_ident()
    # prefix = f'[{this_id} : {this_thread}] '

    reentrant = 0
    wait = 0

    if 1:
        with updater_lock:
            reentrant = updater.get(key) == this_thread
            wait = updater.setdefault(key, this_thread) != this_thread
            # if 1:
            #     print('{} aquire_updater'.format(prefix))
            #     print('{} updater   = {}'.format(prefix, ub.repr2(updater, nl=1)))
            #     print('{} reentrant = {}'.format(prefix, ub.color_text(str(reentrant), "red" if reentrant else "green")))
            #     print('{} wait      = {}'.format(prefix, ub.color_text(str(wait), "red" if wait else "green")))

        if 0:
            if wait:
                with cv:
                    with updater_lock:
                        reentrant = updater.get(key) == this_thread
                        wait = updater.setdefault(key, this_thread) != this_thread
        else:
            while wait:
                with cv:
                    while this_thread != updater.get(key, this_thread):
                        cv.wait()
                    with updater_lock:
                        reentrant = updater.get(key) == this_thread
                        wait = updater.setdefault(key, this_thread) != this_thread

                # if 1:
                # print(prefix + ub.color_text('[wait] in loop', 'blue'))
                #     print(prefix + ub.color_text('[wait] start', 'blue'))
                #     print('{} [wait] updater   = {}'.format(prefix, ub.repr2(updater, nl=1)))
                #     print('{} [wait] reentrant = {}'.format(prefix, ub.color_text(str(reentrant), "red" if reentrant else "green")))
                #     print('{} [wait] wait      = {}'.format(prefix, ub.color_text(str(wait), "red" if wait else "green")))
                #     print(prefix + ub.color_text('[wait] stop', 'blue'))

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
    pool = ub.JobPool('thread', max_workers=4)

    for i in range(100):
        instance_ids = [i % 2 for i  in range(10000)]
        random.shuffle(instance_ids)

        for this_id in instance_ids:
            pool.submit(worker, this_id, 3)

        finished_jobs = [job for job in ub.ProgIter(pool.as_completed(), total=len(pool))]

        for job in finished_jobs:
            if random.random() > 0.5:
                cache.clear()
            try:
                job.result()
            except Exception:
                pass
                # print('ex = {!r}'.format(ex))
        # print('finished_jobs = {!r}'.format(finished_jobs))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_locking.py
    """
    main()
