import math
import numpy as np


def benchmark_bit_conversions():
    # for val in [-0, -1, -3, -4, -9999]:

    test_values = [
        # -1, -2, -3, -4, -8, -32, -290, -9999,
        # 0, 1, 2, 3, 4, 8, 32, 290, 9999,
        4324, 1028, 1024, 3000, -100000,
        999999999999,
        -999999999999,
        2 ** 32,
        2 ** 64,
        2 ** 128,
        2 ** 128,
    ]

    for val in test_values:
        r1 = bit_positions_str(val)
        r2 = bit_positions_numpy(val)
        r3 = bit_positions_lut(val)
        print(f'val={val}')
        print(f'r1={r1}')
        print(f'r2={r2}')
        print(f'r3={r3}')
        print('---')
        assert r1 == r2

    import xdev
    xdev.profile_now(bit_positions_numpy)(val)
    xdev.profile_now(bit_positions_str)(val)
    xdev.profile_now(bit_positions_lut)(val)

    import timerit
    ti = timerit.Timerit(10000, bestof=10, verbose=2)
    for timer in ti.reset('str'):
        for val in test_values:
            bit_positions_str(val)

    for timer in ti.reset('numpy'):
        for val in test_values:
            bit_positions_numpy(val)

    for timer in ti.reset('lut'):
        for val in test_values:
            bit_positions_lut(val)

    for timer in ti.reset('raw_bin'):
        for val in test_values:
            bin(val)

    for timer in ti.reset('raw_bytes'):
        for val in test_values:
            val.to_bytes(val.bit_length(), 'big', signed=True)


def bit_positions_numpy(val):
    """
    Given an integer value, return the positions of the on bits.
    """
    bit_length = val.bit_length() + 1
    length = math.ceil(bit_length / 8.0)  # bytelength
    bytestr = val.to_bytes(length, byteorder='big', signed=True)
    arr = np.frombuffer(bytestr, dtype=np.uint8, count=length)
    bit_arr = np.unpackbits(arr, bitorder='big')
    bit_positions = np.where(bit_arr[::-1])[0].tolist()
    return bit_positions


def bit_positions_str(val):
    is_negative = val < 0
    if is_negative:
        bit_length = val.bit_length() + 1
        length = math.ceil(bit_length / 8.0)  # bytelength
        neg_position = (length * 8) - 1
        # special logic for negatives to get twos compliment repr
        max_val = 1 << neg_position
        val_ = max_val + val
    else:
        val_ = val
    binary_string = '{:b}'.format(val_)[::-1]
    bit_positions = [pos for pos, char in enumerate(binary_string)
                     if char == '1']
    if is_negative:
        bit_positions.append(neg_position)
    return bit_positions


BYTE_TO_POSITIONS = []
pos_masks = [(s, (1 << s)) for s in range(0, 8)]
for i in range(0, 256):
    positions = [pos  for pos, mask in pos_masks if (mask & i)]
    BYTE_TO_POSITIONS.append(positions)


def bit_positions_lut(val):
    bit_length = val.bit_length() + 1
    length = math.ceil(bit_length / 8.0)  # bytelength
    bytestr = val.to_bytes(length, byteorder='big', signed=True)
    bit_positions = []
    for offset, b in enumerate(bytestr[::-1]):
        pos = BYTE_TO_POSITIONS[b]
        if offset == 0:
            bit_positions.extend(pos)
        else:
            pos_offset = (8 * offset)
            bit_positions.extend([p + pos_offset for p in pos])
    return bit_positions


def unpack_bit_positions(val, itemsize=None):
    """
    Given an integer value, return the positions of the on bits.

    Args:
        val (int): a signed or unsigned integer

        itemsize (int | None):
            Number of bytes used to represent the integer. E.g. 1 for a uint8 4
            for an int32. If unspecified infer the smallest number of bytes
            needed, but warning this may produce ambiguous results for negative
            numbers.

    Returns:
        List[int]: the indexes of the 1 bits.

    Note:
        This turns out to be faster than a numpy or lookuptable strategy I
        tried.  See github.com:Erotemic/misc/learn/bit_conversion.py

    Example:
        >>> unpack_bit_positions(0)
        []
        >>> unpack_bit_positions(1)
        [0]
        >>> unpack_bit_positions(-1)
        [0, 1, 2, 3, 4, 5, 6, 7]
        >>> unpack_bit_positions(-1, itemsize=2)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        >>> unpack_bit_positions(9)
        [0, 3]
        >>> unpack_bit_positions(2132)
        [2, 4, 6, 11]
        >>> unpack_bit_positions(-9999)
        [0, 4, 5, 6, 7, 11, 12, 14, 15]
        >>> unpack_bit_positions(np.int16(-9999))
        [0, 4, 5, 6, 7, 11, 12, 14, 15]
        >>> unpack_bit_positions(np.int16(-1))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    """
    is_negative = val < 0
    if is_negative:
        if itemsize is None:
            try:
                bit_length = val.bit_length() + 1
                itemsize = math.ceil(bit_length / 8.0)  # bytelength
            except AttributeError:
                # Probably a numpy type
                itemsize = val.dtype.itemsize
        neg_position = (itemsize * 8) - 1
        # special logic for negatives to get twos compliment repr
        max_val = 1 << neg_position
        val_ = max_val + val
    else:
        val_ = val
    binary_string = '{:b}'.format(val_)[::-1]
    bit_positions = [pos for pos, char in enumerate(binary_string)
                     if char == '1']
    if is_negative:
        bit_positions.append(neg_position)
    return bit_positions


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/bit_conversion.py
    """
    benchmark_bit_conversions()
