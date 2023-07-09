import ubelt as ub
import rich
import asyncio


def main():
    # from kwutil.slugify_ext import smart_truncate
    dpath = ub.Path.appdir('misc/tests/async_executor').ensuredir()

    num = 1000
    print(f'num={num}')
    fpaths = [dpath / f'a_{i}.txt' for i in range(num)]

    def getimpl(mode):
        if mode == 'serial':
            pool = ub.JobPool(mode='serial')
        elif mode == 'thread':
            pool = ub.JobPool(mode='thread', max_workers=4)
        else:
            pool = AsyncJobPool()
        return pool

    for key in ['serial', 'thread', 'async']:
        rich.print(f'[green] Executor: {key}')

        with ub.Timer(f'{key} write text'):
            pool = getimpl(key)
            with pool:
                for fpath in fpaths:
                    pool.submit(fpath.write_text, str(fpath) * 4096)
                results = [f.result() for f in pool.as_completed()]
                # print('results = {}'.format(smart_truncate(ub.urepr(results, nl=0), max_length=128)))

        with ub.Timer(f'{key} delete text'):
            pool = getimpl(key)
            with pool:
                for fpath in fpaths:
                    pool.submit(fpath.delete)
                results = [f.result() for f in pool.as_completed()]
                results
                # print('results = {}'.format(smart_truncate(ub.urepr(results, nl=0), max_length=128)))

    # # 1. Run in the default loop's executor:
    # rich.print('[yellow] Test: AsyncioExectuor (with executor?)')
    # pool = AsyncJobPool()
    # with pool:
    #     for fpath in fpaths:
    #         pool.submit(non_async_worker_func, fpath)
    #     results = [f.result() for f in pool.as_completed()]
    #     print('results = {}'.format(ub.urepr(results, nl=1)))
    #     import concurrent.futures
    #     with concurrent.futures.ThreadPoolExecutor() as tpool:
    #         result = await pool.loop.run_in_executor(tpool, blocking_io)
    # print('default thread pool', result)

    # # 2. Run in a custom thread pool:
    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     result = loop.run_in_executor(
    #         pool, blocking_io)
    #     print('custom thread pool', result)


class AsyncJob:
    _uncomputed = object()

    def __init__(self, func, args, kwargs, parent=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.coroutine = None
        self.parent = parent
        self._result = self._uncomputed

    def submit(self):
        self.coroutine = self._async_run()

    def result(self):
        if self._result is self._uncomputed:
            self._block_for_result()
        return self._result

    def _block_for_result(self):
        import asyncio
        gathered = asyncio.gather(self.coroutine)
        self.parent.loop.run_until_complete(gathered)

    async def _async_run(self):
        self._result = self.func(*self.args, **self.kwargs)
        return self


class AsyncResult:
    def __init__(self, data):
        self.data = data

    def result(self):
        return self.data


class AsyncJobPool:
    def __init__(self):
        self._jobs = []
        self._loop = None
        self._coroutine = None

    def __enter__(self):
        self.loop = asyncio.get_event_loop()
        return self

    def __exit__(self, ex_type, ex_value, tb):
        return self

    def submit(self, func, *args, **kwargs):
        job = AsyncJob(func, args, kwargs, self)
        job.submit()
        self._jobs.append(job)

    def as_completed(self):
        _coroutine = _async_as_completed(self._jobs)
        gathered = asyncio.gather(_coroutine)
        results, = self.loop.run_until_complete(gathered)
        yield from results


async def _async_as_completed(jobs):
    futures = []
    for job in jobs:
        f = job.coroutine
        futures.append(f)
    results = []
    for f in asyncio.as_completed(futures):
        results.append(await f)
    return results


def non_async_worker_func(fpath):
    # print(f'[worker] fpath={fpath}')
    fpath = ub.Path(fpath)
    # print(f'[worker] fpath={fpath}')
    fpath.write_text(f'my name is {fpath}')
    return {'fpath': fpath, 'content': fpath.read_text()}


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_async_executor.py
    """
    main()
