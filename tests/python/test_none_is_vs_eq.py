"""
When comparing a variable to ``None``, you should always use the ``is``
operator:

.. code:: python

    var is None

Instead of of the ``==`` operator.

.. code:: python

    var == None


Running this script demonstrates 1. that this is this case, and 2. why this is
the case.

In terms or raw timings we see using ``is`` gives a slight, but effectively
free speed improvement.

    Timed equal_none-vs-dict for: 1000000 loops, best of 1000
        body took: 159.573 ms
        time per loop: best=139.000 ns, mean=143.454 ± 1.8 ns
    Timed is_none-vs-dict for: 1000000 loops, best of 1000
        body took: 149.005 ms
        time per loop: best=130.000 ns, mean=134.015 ± 1.3 ns
    Timed equal_none-vs-None for: 1000000 loops, best of 1000
        body took: 157.017 ms
        time per loop: best=132.000 ns, mean=139.060 ± 2.8 ns
    Timed is_none-vs-None for: 1000000 loops, best of 1000
        body took: 150.105 ms
        time per loop: best=130.000 ns, mean=133.617 ± 1.3 ns

The final average rankings are:

    'is_none-vs-None'   : 1.3361-07,
    'is_none-vs-dict'   : 1.3401-07,
    'equal_none-vs-None': 1.3906-07,
    'equal_none-vs-dict': 1.4345-07,


We can see why this is by inspecting the Python disassembly:

.. code::

    --- equal_none ---
      5           2 LOAD_FAST                0 (var)
                  4 LOAD_CONST               0 (None)
                  6 COMPARE_OP               2 (==)

    --- is none ---
      8           2 LOAD_FAST                0 (var)
                  4 LOAD_CONST               0 (None)
                  6 IS_OP                    0

The difference is the ``COMPARE_OP`` instruction versus the ``IS_OP``
instruction, the later of which is simpler because it only compares memory
addresses, and as such it is nearly always faster. For singletons like ``None``
using memory address comparison is always equivalent to full comparisons, so
if you are taking the time to read this and learn about the differences between
``is`` and ``==`` (i.e. ``__eq__``), then you may as well make a habit of
writing code with that optimization.

"""


def compare_is_vs_equal_disassembly():
    import dis

    def equal_none(var):
        return var == None  # NOQA

    def is_none(var):
        return var is None

    print('--- equal_none ---')
    dis.dis(equal_none)
    print('--- is none ---')
    dis.dis(is_none)


def time_is_vs_equal():
    import timerit
    ti = timerit.Timerit(1_000_000, bestof=1_000, verbose=3)

    var = dict()
    for timer in ti.reset('equal_none-vs-dict'):
        with timer:
            var == None  # NOQA
    for timer in ti.reset('is_none-vs-dict'):
        with timer:
            var is None

    var = None
    for timer in ti.reset('equal_none-vs-None'):
        with timer:
            var == None  # NOQA
    for timer in ti.reset('is_none-vs-None'):
        with timer:
            var is None

    import ubelt as ub
    print(ub.urepr(ti.rankings['mean'], align=':'))


def main():
    time_is_vs_equal()
    compare_is_vs_equal_disassembly()


if __name__ == '__main__':
    """
    CommandLine:
        python test_none_compare.py
    """
    main()
