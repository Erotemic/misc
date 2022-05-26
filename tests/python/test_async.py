"""
Benchmark asyncio versus concurrent.futures versus serial image loading

Even with uvloop asyncio falls short

Results:
    Timed best=64.301 ms, mean=66.257 ± 1.6 ms for concurrent
    Timed best=124.220 ms, mean=134.891 ± 7.6 ms for load_asyncio_pure_python
    Timed best=110.672 ms, mean=115.680 ± 2.8 ms for load_asyncio_with_uvloop
    Timed best=83.365 ms, mean=86.972 ± 3.3 ms for serial

Requirements:
    timerit
    pooch
    scikit-image
    aiofiles
    uvloop

    pip install aiofiles pooch scikit-image
"""
import concurrent.futures
import aiofiles
import asyncio


def load_datafile(count, fpath):
    with open(fpath, 'rb') as file_:
        return (count, file_.read()[0:10])


async def async_load_datafile(count, fpath):
    async with aiofiles.open(fpath, 'rb') as file_:
        return (count, (await file_.read())[0:10])


def load_serial(fpaths):
    for count, fpath in enumerate(fpaths):
        yield load_datafile(count, fpath)


def load_concurrent(fpaths):
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(load_datafile, count, fpath) for count, fpath in enumerate(fpaths)]
        for f in futures:
            yield f.result()


async def async_worker_load_files(fpaths):
    futures = []
    for count, fpath in enumerate(fpaths):
        futures.append(async_load_datafile(count, fpath))

    finished = asyncio.as_completed(futures)
    images = []
    for f in finished:
        images.append(await f)
    return images


def load_asyncio_pure_python(fpaths):
    loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    coroutine = async_worker_load_files(fpaths)
    gathered = asyncio.gather(coroutine)
    result, = loop.run_until_complete(gathered)
    for item in result:
        yield item


def load_asyncio_with_uvloop(fpaths):
    import uvloop
    uvloop.install()
    loop = asyncio.get_event_loop()
    # loop = uvloop.new_event_loop()
    # asyncio.set_event_loop(loop)
    coroutine = async_worker_load_files(fpaths)
    gathered = asyncio.gather(coroutine)
    result, = loop.run_until_complete(gathered)
    for item in result:
        yield item


def main():
    import timerit
    from os.path import join
    from skimage import data as skimage_data
    from skimage.data import image_fetcher

    skimage_data.download_all()
    fpaths = [join(image_fetcher.path, fname)
              for fname in image_fetcher.registry.keys()
              if fname.endswith(('.tif', '.png', '.jpg'))]

    # Load a lot of files
    fpaths = fpaths * 15

    if 0:
        # Sanity check
        counts, images = zip(*list(load_serial(fpaths)))
        print('counts = {!r}'.format(counts))
        counts, images = zip(*list(load_concurrent(fpaths)))
        print('counts = {!r}'.format(counts))
        counts, images = zip(*list(load_asyncio_pure_python(fpaths)))
        print('counts = {!r}'.format(counts))

    ti = timerit.Timerit(50, bestof=3, verbose=1)
    for timer in ti.reset('concurrent'):
        with timer:
            list(load_concurrent(fpaths))

    for timer in ti.reset('load_asyncio_pure_python'):
        with timer:
            list(load_asyncio_pure_python(fpaths))

    for timer in ti.reset('load_asyncio_with_uvloop'):
        with timer:
            list(load_asyncio_with_uvloop(fpaths))

    for timer in ti.reset('serial'):
        with timer:
            list(load_serial(fpaths))

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_async.py
    """
    main()
