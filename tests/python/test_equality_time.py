"""
Inspired by https://www.youtube.com/watch?v=XThL0LP3RjY

https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/061_time_to_hack_cracking_passwords_using_timing_information_secure_python/timing_attack.py
"""


def main():
    import timerit
    import ubelt as ub
    import random
    import string

    # expected = "58178059833426840615453390153965"
    length = 20
    expected = ''.join(random.choices(string.printable, k=length))

    def flip_char(text, pos):
        old = text[pos]
        new = random.choice(string.printable)
        while new == old:
            pass
        before = text[:pos - 1]
        after = text[pos:]
        return before + new + after

    variants = dict(
        ne_first=flip_char(expected, 0),
        ne_mid=flip_char(expected, length // 2),
        ne_last=flip_char(expected, length - 1),
        too_long='F' * len(expected) * 10,
        too_short='F',
        correct=expected,
    )

    ti = timerit.Timerit(10000000, bestof=10, verbose=2)

    for key, value in variants.items():
        for _ in ti.reset(key):
            value == expected

    print('ti.rankings = {}'.format(ub.repr2(
        ti.rankings['min'], nl=2, align=':')))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/test_equality_time.py
    """
    main()
