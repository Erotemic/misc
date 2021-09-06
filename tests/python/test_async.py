"""
Benchmark asyncio versus concurrent.futures versus serial image loading

Results:
    Timed best=128.881 ms, mean=142.050 ± 4.8 ms for concurrent
    Timed best=346.830 ms, mean=372.968 ± 11.7 ms for asyncio
    Timed best=188.439 ms, mean=190.456 ± 0.8 ms for serial

Requirements:
    timerit
    pooch
    skimage
    aiofiles
"""
import concurrent.futures
import aiofiles
import asyncio


def load_datafile(count, fpath):
    with open(fpath, 'rb') as file_:
        return (count, file_.read()[0:10])


async def aload_datafile(count, fpath):
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


async def _load_asyncio(fpaths):
    futures = []
    for count, fpath in enumerate(fpaths):
        futures.append(aload_datafile(count, fpath))

    finished = asyncio.as_completed(futures)
    images = []
    for f in finished:
        images.append(await f)
    return images


def load_asyncio(fpaths):
    loop = asyncio.get_event_loop()
    coroutine = _load_asyncio(fpaths)
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
        counts, images = zip(*list(load_asyncio(fpaths)))
        print('counts = {!r}'.format(counts))

    ti = timerit.Timerit(100, bestof=3, verbose=1)
    for timer in ti.reset('concurrent'):
        with timer:
            list(load_concurrent(fpaths))

    for timer in ti.reset('asyncio'):
        with timer:
            list(load_asyncio(fpaths))

    for timer in ti.reset('serial'):
        with timer:
            list(load_serial(fpaths))

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_async.py
    """
    main()
