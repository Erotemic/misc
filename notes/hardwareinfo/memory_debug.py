
def checker():
    # This is to help me debug my bad ram
    import pint
    import numpy as np
    reg = pint.UnitRegistry()

    # Total ram
    total = (64 * reg.Unit('gibibyte')).to('gigabyte')
    total = (64 * reg.Unit('gigabyte')).to('gibibyte')

    # Addresses of the edges of each stick
    address_edges = np.linspace(0, total, 4 + 1).to('byte').astype(int)

    for idx, edge in enumerate(address_edges):
        print(f' * 0x{edge.m:09X} - {edge.to("gigabyte")}')

    verified_ok_ranges = [
        ((0x000000000 * reg.byte), (0x600000000 * reg.byte)),

        ((0x700000000 * reg.byte), (0xE00000000 * reg.byte)),

        ((0xE24000000 * reg.byte), (0x1060000000 * reg.byte)),
        # ((0xF00000000 * reg.byte), (0x1060000000 * reg.byte)),
    ]

    for ok_range in verified_ok_ranges:
        for ok_pos in ok_range:
            print(f' * 0x{ok_pos.m:09X} - {ok_pos.to("gigabyte")}')
            idx = np.searchsorted(address_edges, ok_pos.to('bytes'))
            edge1 = address_edges[idx - 1].to('gigabytes')
            try:
                edge2 = address_edges[idx].to('gigabytes')
            except Exception:
                edge2 = ok_pos
            rel_pos = ok_pos - edge1
            rel_frac = (rel_pos) / (edge2 - edge1)
            print('ok_pos = {!r}'.format(ok_pos))
            print('edge1 = {!r}'.format(edge1))
            print('edge2 = {!r}'.format(edge2))
            print('rel_pos = {!r}'.format(rel_pos))
            print('rel_frac = {!r}'.format(rel_frac))
            print('-----')

    # These are addresses that had errors
    error_positions = [
        ((0x620030004 * reg.byte)),
        ((0x623FEFFFC * reg.byte)),
        ((0xE2001121C * reg.byte)),
        ((0xE23016978 * reg.byte)),
        ((0xE23f409b4 * reg.byte)),
    ]
    # ((0x1060000000 * reg.byte).to('gigabyte'))
    for error_pos in error_positions:
        print(f' * 0x{error_pos.m:09X} - {error_pos.to("gigabyte")}')
        idx = np.searchsorted(address_edges, error_pos)
        edge1 = address_edges[idx - 1].to('gigabyte')
        edge2 = address_edges[idx].to('gigabytes')
        rel_pos = error_pos.to('gigabyte') - edge1
        rel_frac = (rel_pos) / (edge2 - edge1)
        print('error_pos = {!r}'.format(error_pos.to('gigabyte')))
        print('edge1 = {!r}'.format(edge1))
        print('edge2 = {!r}'.format(edge2))
        print('rel_pos = {!r}'.format(rel_pos))
        print('rel_frac = {!r}'.format(rel_frac))
        print('-----')

    # (0x600000000 * reg.byte).to('gigabyte')

    # https://unix.stackexchange.com/questions/75059/how-to-blacklist-a-correct-bad-ram-sector-according-to-memtest86-error-indicati
    # https://askubuntu.com/questions/908925/how-do-i-tell-ubuntu-not-to-use-certain-memory-addresses

    # https://stackoverflow.com/questions/8213671/mmap-operation-not-permitted

    # Example

    # The second parameter is a mask.
    # You put 1s where the address range you want shares the same values
    # You put 0s where it will vary.

    import numpy as np
    start = np.uint64(0x7DDF0000)
    stop  = np.uint64(0x7DDF4000) - np.uint64(1)
    target = np.uint64(0xffffc000)

    import numpy as np
    nbytes = 64
    dtype = np.uint64
    # Starting bad mem address range
    start = dtype(0x7DDF0000)
    # Subtract 1 because to make the stop range inclusive instead of exclusive
    stop  = dtype(0x7DDF4000) - dtype(1)

    def xnor(a, b):
        return ~(a ^ b)

    def find_pos_of_leftmost_sig_zero(a, nbytes=64):
        """
        Given a bit string like, we find the position of the first zero bit we
        see coming from the left, such that we can right-bitshift to it to the

            11111110110110
                   ^

        Example:
            >>> nbytes = 32
            >>> vals = [0b0, 0b1, 0b1011, 0b1001]
            >>> for a in vals:
            >>>     print('-----')
            >>>     pos = find_pos_of_leftmost_sig_zero(a, nbytes)
            >>>     print(f'a = {a:032b}')
            >>>     print('    ' + ' ' * (nbytes - pos - 1) + '^')
            >>>     print(f'pos = {pos}')
            -----
            a = 00000000000000000000000000000000
                                               ^
            pos = 0
            -----
            a = 00000000000000000000000000000001
                                               ^
            pos = 0
            -----
            a = 00000000000000000000000000001011
                                             ^
            pos = 2
            -----
            a = 00000000000000000000000000001001
                                             ^
            pos = 2
        """
        # not really a fast op, but it works well enough There is a semi-corner
        # case at 1 and 0, but it doesnt change how we use it
        binstr = ('{:0' + str(nbytes) + 'b}').format(a)
        try:
            leftmost_one = binstr.index('1')
        except ValueError:
            return 0
        try:
            leftmost_sig_zero = binstr[leftmost_one:].index('0') + leftmost_one + 1
        except Exception:
            return 0
        # Flip string indexes to bit indexes
        return nbytes - leftmost_sig_zero

    # Find all the bits in common
    common = xnor(start, stop)

    # Find the position of the first zero (non-common bit) we see from the left
    shift = dtype(find_pos_of_leftmost_sig_zero(common, nbytes))

    # Right then left shift to zero out the tail, which constructs the mask
    mask = (common >> shift) << (shift)

    print(f'start  = 0b{start:64b} = 0x{start:16x}')
    print(f'stop   = 0b{stop:64b} = 0x{stop:16x}')
    print(f'common = 0b{common:64b} = 0x{common:16x}')
    print(f'mask   = 0b{mask:64b} = 0x{mask:16x}')

    print('--')
    print(f'mask = ' + hex(mask))

    print(f'0b{target:64b}')

    # start = 0x7DDF0000
    0b01111101110111110000000000000000
    # stop = 0x7DDF4000
    0b01111101110111110100000000000000

    0b0111110111011111 0100 0000 0000 0000
    0b1111101110111110100000000000000
    # Common =
    0b11111111111111111011111111111111

    # 0xffff8000
    0b11111111111111111000000000000000
    # 0xffffc000
    0b11111111111111111100000000000000

    0b1111111111111111111111111111111111111111111111111011111111111111
                     b100000000000000
    0b1111111111111111000000000000000
    hex(0b1111111111111111100000000000000)


    # Real

    ((0x700000000 - 0x600000000) * reg.byte).to('megabyte')
    ((0xE24000000 - 0xE00000000) * reg.byte).to('megabyte')

    find_grub_badram_format(0x700000000, 0x600000000)

    0b11000000000000000000000000000000000
    0b11100000000000000000000000000000000

    start = 0x600000000
    stop = 0x700000000
    mask = start & stop
    start & mask

    print('0X{:09X}'.format(start ^ stop))

    '''
    # Using the memtester trick does not work if the kernel does not
    # allow users to address physical RAM space.

    sudo memtester -p 0x600000000 4295M 128
    sudo memtester -p 0xE00000000 604M 128
    '''


def find_grub_badram_format(start, stop):
    import numpy as np
    nbytes = 64
    dtype = np.uint64
    # Starting bad mem address range
    start = dtype(start)
    # Subtract 1 because to make the stop range inclusive instead of exclusive
    stop  = dtype(stop) - dtype(1)

    def xnor(a, b):
        return ~(a ^ b)

    def find_pos_of_leftmost_sig_zero(a, nbytes=64):
        """
        Given a bit string like, we find the position of the first zero bit we
        see coming from the left, such that we can right-bitshift to it to the

            11111110110110
                   ^

        Example:
            >>> nbytes = 32
            >>> vals = [0b0, 0b1, 0b1011, 0b1001]
            >>> for a in vals:
            >>>     print('-----')
            >>>     pos = find_pos_of_leftmost_sig_zero(a, nbytes)
            >>>     print(f'a = {a:032b}')
            >>>     print('    ' + ' ' * (nbytes - pos - 1) + '^')
            >>>     print(f'pos = {pos}')
            -----
            a = 00000000000000000000000000000000
                                               ^
            pos = 0
            -----
            a = 00000000000000000000000000000001
                                               ^
            pos = 0
            -----
            a = 00000000000000000000000000001011
                                             ^
            pos = 2
            -----
            a = 00000000000000000000000000001001
                                             ^
            pos = 2
        """
        # not really a fast op, but it works well enough There is a semi-corner
        # case at 1 and 0, but it doesnt change how we use it
        binstr = ('{:0' + str(nbytes) + 'b}').format(a)
        try:
            leftmost_one = binstr.index('1')
        except ValueError:
            return 0
        try:
            leftmost_sig_zero = binstr[leftmost_one:].index('0') + leftmost_one + 1
        except Exception:
            return 0
        # Flip string indexes to bit indexes
        return nbytes - leftmost_sig_zero

    # Find all the bits in common
    common = xnor(start, stop)

    # Find the position of the first zero (non-common bit) we see from the left
    shift = dtype(find_pos_of_leftmost_sig_zero(common, nbytes))

    # Right then left shift to zero out the tail, which constructs the mask
    mask = (common >> shift) << (shift)

    print(f'start  = 0b{start:64b} = 0x{start:16x}')
    print(f'stop   = 0b{stop:64b} = 0x{stop:16x}')
    print(f'common = 0b{common:64b} = 0x{common:16x}')
    print(f'mask   = 0b{mask:64b} = 0x{mask:16x}')

    print('--')
    print(f'mask = ' + hex(mask))

    badram_format = f'0x{start:0{16}x},0x{mask:#0{16}x}'
    print(badram_format)
