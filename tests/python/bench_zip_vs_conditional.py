def bench_zip_vs_conditional():

    import itertools as it

    iterable = it.repeat(1)
    max_num = 10000

    def clip_iterable_with_if(iterable, max_num):
        for idx, item in enumerate(iterable):
            if idx >= max_num:
                break
            yield item

    def clip_iterable_with_zip(iterable, max_num):
        for idx, item in zip(range(max_num), iterable):
            yield item

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)

    for timer in ti.reset('clip_iterable_with_if'):
        with timer:
            list(clip_iterable_with_if(iterable, max_num))

    # WINNER
    for timer in ti.reset('clip_iterable_with_zip'):
        with timer:
            list(clip_iterable_with_zip(iterable, max_num))

    # Timed clip_iterable_with_zip for: 100 loops, best of 10
    #     time per loop: best=61.563 µs, mean=63.385 ± 0.7 µs
    # Timed clip_iterable_with_if for: 100 loops, best of 10
    #     time per loop: best=124.244 µs, mean=130.471 ± 3.7 µs


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/python_tests/bench_zip_vs_conditional.py
    """
    bench_zip_vs_conditional()
