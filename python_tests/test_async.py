import concurrent.futures
import aiofiles
"""
TODO: move to 3.6

figure out why asyncio not working well
"""


def load_datafile(count, fpath):
    with open(fpath, 'rb') as file_:
        return (count, file_.read()[0:10])


async def aload_datafile(count, fpath):
    # with open(fpath, 'rb') as file_:
    #     return (count, file_.read()[0:10])
    async with aiofiles.open(fpath, 'rb') as file_:
        return (count, (await file_.read())[0:10])


def load_serial(fpaths):
    for count, fpath in enumerate(fpaths):
        yield load_datafile(count, fpath)


def load_concurrent(fpaths):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(load_datafile, count, fpath) for count, fpath in enumerate(fpaths)]
        for f in futures:
            yield f.result()
        # images = [f.result() for f in concurrent.futures.as_completed(futures)]
        # return images


async def _load_asyncio(fpaths):
    futures = []
    for count, fpath in enumerate(fpaths):
        futures.append(aload_datafile(count, fpath))

    finished = asyncio.as_completed(futures)
    images = []
    for f in finished:
        images.append(await f)
    return images
    # images = [f.result() for f in finished]
    # return images


def load_asyncio(fpaths):
    loop = asyncio.get_event_loop()
    coroutine = _load_asyncio(fpaths)
    gathered = asyncio.gather(coroutine)
    result, = loop.run_until_complete(gathered)
    for item in result:
        yield item
    # loop.close()


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/misc/python_tests/test_async.py
    """
    import asyncio
    import glob

    fpaths = glob.glob('/home/joncrall/data/ibeis/work/PZ_MTEST/_ibsdb/images/*.jpg')
    fpaths = fpaths

    counts, images = zip(*list(load_serial(fpaths)))
    print('counts = {!r}'.format(counts))
    counts, images = zip(*list(load_concurrent(fpaths)))
    print('counts = {!r}'.format(counts))
    counts, images = zip(*list(load_asyncio(fpaths)))
    print('counts = {!r}'.format(counts))

    import ubelt
    for timer in ubelt.Timerit(10, label='concurrent'):
        with timer:
            list(load_concurrent(fpaths))

    import ubelt
    for timer in ubelt.Timerit(10, label='asyncio'):
        with timer:
            list(load_asyncio(fpaths))

    import ubelt
    for timer in ubelt.Timerit(10, label='serial'):
        with timer:
            list(load_serial(fpaths))

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test())
