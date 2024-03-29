"""
An attempt at maintaining structured information about hardware I've bought,
used, or have been interested in.

References:
    https://www.cpu-world.com/cgi-bin/CPUID.pl
    https://www.techpowerup.com/cpu-specs/

    https://www.displaydb.com/

    https://routerchart.com/

    https://wiki.debian.org/Hardware/Database
    https://github.com/linuxhw/


    Sandy Bridge Release MSRP
    https://hw-lab.com/price-and-release-day-of-intel-sandy-bridge-cpu.html

    https://www.techpowerup.com/cpu-specs/

"""
import pint
import dateutil
ureg = pint.UnitRegistry()


def define2(n):
    ureg.define(f'{n} = []')
    return ureg.Unit(n)

dollars = define2('dollars')
pixels = define2('pixels')

ms = ureg.Unit('milliseconds')
mm = ureg.Unit('millimeters')
MHz = ureg.Unit('megahertz')
GHz = ureg.Unit('gigahertz')
Hz = ureg.Unit('hertz')
MB = ureg.Unit('megabyte')
TB = ureg.Unit('terabyte')
inches = ureg.Unit('inches')
degrees = ureg.Unit('degrees')
watts = ureg.Unit('watts')


class Currency:
    """
    Records how much currency something was worth at a particular date.

    Currency fluctuates in value, so recording the MSRP at a given date helps
    convert between values in one year and values in another.
    """
    def __init__(self, amount, date=None):
        self.amount = amount
        self.date = date

    def __repr__(self):
        if self.date:
            return f'{self.amount} @ {self.date}'
        else:
            return f'{self.amount}'

    __str__ = __repr__

    def __matmul__(self, date):
        if isinstance(date, str):
            date = dateutil.parser.parse(date)
        self.date = date
        return self


items = [
    {
        'name': 'EVGA GeForce GTX 1080 Ti FTW3',
        'type': 'gpu',
        'part_number': '11G-P4-6696-KR',
        'spec_url': 'https://www.evga.com/products/specs/gpu.aspx?pn=1190fbf7-7f11-465d-b303-cab0e50fbdc6',
        'memory': 11264 * MB,
        'clock': {
            'base': 1569 * MHz,
            'boost': 1683 * MHz,
        },
        'cuda_cores': 3584,
        'dimensions': {
            'length': 299.72 * mm,
            'height': 142.69 * mm,
            'pcie_slots': 2,
        }
    },

    {
        'name': 'EVGA GeForce GTX 1080 Ti SC2',
        'type': 'gpu',
        'part_number': '11G-P4-6593-KR',
        'spec_url': 'https://www.evga.com/products/specs/gpu.aspx?pn=61e6d689-506e-45df-8202-b49614e9d54d',
        'msrp': Currency(769.99 * dollars) @ '2017',
        'cuda_cores': 3584,
        'memory': 11264 * MB,
        'clock': {
            'base': 1556 * MHz,
            'boost': 1670 * MHz,
        },
        'dimensions': {
            'length': 269.2 * mm,
            'height': 118.48 * mm,
            'pcie_slots': 2,
        }
    },

    {
        'name': 'EVGA GeForce RTX 3090 FTW3',
        'type': 'gpu',
        'part_number': '24G-P5-3985-KR',
        'spec_url': 'https://www.evga.com/products/Specs/GPU.aspx?pn=f62c60ad-fd39-4cca-ab59-ead120bdff04',
        'cuda_cores': 10496,
        'memory': 24576 * MB,
        'clock': {
            'boost': 1740 * MHz,
        },
        'dimensions': {
            'length': 300 * mm,
            'height': 136.75 * mm,
            'pcie_slots': 2.75,
        }
    },

    {
        'name': 'Dell Ultrasharp U2718Q',
        'msrp': 600.00 * dollars,
        'type': 'monitor',
        'model': 'U2718Q',
        'size': 27 * inches,
        'spec_url': 'https://www.dell.com/si/business/p/dell-u2718q-monitor/pd',
        'display': {
            'panel_type': 'IPS',  # in-plane-switching
            'max_resolution': {
                'width': 3840 * pixels,
                'height': 2160 * pixels,
            },
            'refresh_rate': 60 * Hz,
            'response_time': 5 * ms,
            'dimensions': {
                'width': 23.49 * inches,
                'height': 13.21 * inches,
                'aspect_ratio': 16 / 9,
            },
            'viewing_angle':  {'vertical': 178 * degrees, 'horizontal': 178 * degrees},

        },
        'sucessors': [
            'U2720QM',
        ]
    },

    {
        'name': 'LG 27UK650-W',
        'msrp': 500.00 * dollars,
        'type': 'monitor',
        'model': '27UK650-W',
        'size': 27 * inches,
        'spec_url': 'https://www.lg.com/us/monitors/lg-27UK650-W-4k-uhd-led-monitor#',
        'display': {
            'panel_type': 'IPS',  # in-plane-switching
            'response_time': 5 * ms,
            'max_resolution': {
                'width': 3840 * pixels,
                'height': 2160 * pixels,
            },
            'color_depth': '10bit(8bit + A-FRC)',
            'refresh_rate': 60 * Hz,
            'viewing_angle':  {'vertical': 178 * degrees, 'horizontal': 178 * degrees},
        },
    },

    {
        'name': 'LG 27GL850',
        'msrp': 379.99 * dollars,
        'type': 'monitor',
        'model': '27UK650-W',
        'size': 27 * inches,
        'spec_url': 'https://www.lg.com/us/monitors/lg-27GL850-B-gaming-monitor',
        'display': {
            'panel_type': 'IPS',  # in-plane-switching
            'response_time': 1 * ms,
            'max_resolution': {
                'width': 2560 * pixels,
                'height': 1440 * pixels,
            },
            'color_depth': 1.07e9,
            'refresh_rate': 144 * Hz,
            'viewing_angle':  {'vertical': 178 * degrees, 'horizontal': 178 * degrees},
        },
    },

    {
        'name': 'LG 27GL83A 27',
        'msrp': 500.00 * dollars,
        'type': 'monitor',
        'model': '27GL83A-B',
        'size': 27 * inches,
        'spec_url': 'https://www.lg.com/us/monitors/lg-27gl83a-b-gaming-monitor',
        'display': {
            'panel_type': 'Nano IPS',  # in-plane-switching
            'response_time': 1 * ms,
            'max_resolution': {
                'width': 2560 * pixels,
                'height': 1440 * pixels,
            },
            'color_depth': 1.07e9,
            'refresh_rate': 144 * Hz,
            'viewing_angle':  {'vertical': 178 * degrees, 'horizontal': 178 * degrees},
        },
    },

    {
        'name': 'EVGA T2 1600 W 80+ Titanium Certified Fully Modular ATX Power Supply',
        'part_number': '220-T2-1600',
        'type': 'psu',
        'power': 1600 * watts,
        'efficiency_rating': 'titanium',
        'msrp': Currency(579.99 * dollars) @ '2021-08-07',
        'references': [
            'https://www.evga.com/products/product.aspx?pn=220-T2-1600-X1',
            'https://www.techpowerup.com/review/evga-supernova-t2-1600/6.html',
        ]
    },

    {
        'name': 'EVGA SuperNOVA 1000 T2, 80+ TITANIUM 1000W',
        'part_number': '220-T2-1000',
        'type': 'psu',
        'power': 1000 * watts,
        'efficiency_rating': 'titanium',
        'msrp': Currency(349.99 * dollars) @ '2021-08-07',
        'references': [
            'https://www.evga.com/products/product.aspx?pn=220-T2-1000-X1',
        ]
    },

    {
        'name': 'Intel Core i7-2600K 3.4 GHz Quad-Core Processor',
        'part_number': 'i7-2600K',
        'type': 'cpu',
        'sockets': ['LGA1155'],
        'power': 95 * watts,
        'msrp': Currency(315.99 * dollars) @ '2011-01-09',
        'total_cores': 4,
        'total_threads': 8,
        'clock': {
            'base': 3.4 * GHz,
            'turbo': 3.8 * GHz,
        },
        'references': [
            'https://hw-lab.com/price-and-release-day-of-intel-sandy-bridge-cpu.html',
            'https://ark.intel.com/content/www/us/en/ark/products/52214/intel-core-i72600k-processor-8m-cache-up-to-3-80-ghz.html',
        ]
    },

    {
        'name': 'Asus P8P67 Pro ATX LGA1155 Motherboard',
        'type': 'mobo',
        'msrp': Currency(179.99 * dollars) @ '2011',
        'references': [
            'https://uk.pcmag.com/chipsets-processors/20823/asus-p8p67-pro',
            'https://web.archive.org/web/20201026195622/https://uk.pcmag.com/chipsets-processors/20823/asus-p8p67-pro',
        ]
    },

    {
        'name': 'Seagate BarraCuda Pro SATA HDD 10TB 7200RPM 6Gb/s 256MB Cache 3.5-Inch Internal Hard Drive',
        'type': 'hdd',
        'model': 'ST10000DM0004',
        'brand': 'seagate',
        'form': 3.5 * inches,
        'hdi': 'SATA',
        'capacity': 10 * TB,
        'msrp': Currency(254.99 * dollars) @ '2022',
        'sales': [
            {'price': Currency(185.00 * dollars) @ '2022', 'condition': 'renewed', 'seller': 'oceanside store'},
        ],
        'references': [
            'https://www.amazon.com/dp/B07MWCVMXJ?ref=ppx_yo2ov_dt_b_product_details&th=1',
        ]
    },


]
