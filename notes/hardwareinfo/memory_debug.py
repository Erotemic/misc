
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

        ((0xE30000000 * reg.byte), (0x1060000000 * reg.byte)),

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
