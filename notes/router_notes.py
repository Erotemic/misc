def router_notes():
    """

    https://en.wikipedia.org/wiki/Gigabit_Ethernet

    Ethernet connections:

        100BASE-TX 100Mbps Ethernet over Cat 5

        1000BASE-TX

        40GBASE-T 40Gbps Ethernet over Cat 8

        2.5GBASE

        2.5GBASE-T and 5GBASE-T can be deployed at a cable length of up to 100 m on Cat 5e or better cables.[5]

        Cat 5e - 2.5Gb
        Cat 6 -  5Gb
        Cat 6a - 10Gb

        https://en.wikipedia.org/wiki/IEEE_802.11

        IEEE 802.11ac-2013 or 802.11ac - WIFI 5
        IEEE 802.11ax-2021 or 802.11ax - WIFI 6
    """

    import pint
    ureg = pint.UnitRegistry()
    ureg.define('dollar = []')

    dollar = ureg.dollar

    s = ureg.Unit('second')
    h = ureg.Unit('hour')
    MB = ureg.Unit('megabyte')
    GB = ureg.Unit('gigabyte')
    TB = ureg.Unit('terabyte')

    ((4 * TB) / (11 * MB / s)).to(h)

    Mbps = ureg.Unit('megabit/second')
    Gbps = ureg.Unit('gigabit/second')
    MBps = ureg.Unit('megabyte/second')
    GBps = ureg.Unit('gigabyte/second')

    dollars = ureg.Unit('dollars')

    (100 * Mbps).to(Mbps)
    (1000 * Mbps).to(Mbps)
    (2.5 * Gbps).to(Mbps)
    (2.5 * Gbps).to(Mbps)

    # R7350

    router_wifi_rates = {
        'Nighthawk X6 - R8000': {
            'wifi': (3200 * Mbps).to(MBps),
            'wired': (1 * Gbps).to(MBps),
            'price': 150 * dollars
        },
        'Nighthawk 12-Stream AX12 Wifi 6 Router (RAX200)': {
            'wired': (2.5 * Gbps).to(MBps),
            'wifi': (10.8 * Gbps).to(MBps),
            'price': 500 * dollar,
        },
        'ROG Rapture WiFi 6E - GT-AXE11000': {
            'wired': (2.5 * Gbps).to(MBps),
            'wifi': (11000 * Mbps).to(MBps),
            'price': 870 * dollar},
    }

    print('router_wifi_rates = {}'.format(ub.repr2(router_wifi_rates, nl=3)))
