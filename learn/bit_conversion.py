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


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/bit_conversion.py
    """
    benchmark_bit_conversions()
