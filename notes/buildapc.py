
"""
Reviews:
    https://www.gamersnexus.net/reviews/hwreviews

Lists:
    https://pcpartpicker.com/user/erotemic/saved/qHnY99
    https://pcpartpicker.com/user/erotemic/saved/DFYMbv
    https://pcpartpicker.com/user/erotemic/saved/gcyjZL



References:
    https://pcpartpicker.com/products/cpu/#sort=-rating&s=61&page=1
    https://pcpartpicker.com/list/
    https://www.logicalincrements.com/


CPU Options:

    Top Picks:

    Intel Core i9-9900KF   8  3.6 GHz  5 GHz     95 W  None  Yes   (12) $359.99 - good value budget, lower power

    Intel Core i9-10900X  10  3.7 GHz  4.7 GHz  165 W  None  Yes   (0)  $562.00 - CascadeLake deep learning optimizations

    Others:

    Intel Core i9-10900KF 10  3.7 GHz  5.3 GHz  125 W  None  Yes   (3)  $529.99
    Intel Core i9-10920X  12  3.5 GHz  4.8 GHz  165 W  None  Yes   (0)  $642.00
    Intel Core i9-9920X   12  3.5 GHz  4.4 GHz  165 W  None  Yes   (1)  $669.60
    Intel Core i9-9900X   10  3.5 GHz  4.4 GHz  165 W  None  Yes   (1)  $602.00
    Intel Core i9-9920X   12  3.5 GHz  4.4 GHz  165 W  None  Yes   (0)  $478.50
    Intel Core i9-9900X   10  3.5 GHz  4.4 GHz  165 W  None  Yes   (0)  $564.54

Coolers:

    Noctua is one of the best brands. The NH-D15 is considered a classic / staple.

    NOTE: you need to check your RAM to make sure it has space when using the D15

    NZXT Kraken X61 - 800 - 2000 RPM  20 - 37 dB    280 mm   (132)
    Noctua NH-D15   - 300 - 1500 RPM  19.2 - 24.6 dB       (120)  $89.95

    Noctua NH-D15 CHROMAX.BLACK 82.52 CFM CPU Cooler - https://pcpartpicker.com/product/84MTwP/noctua-nh-d15-chromaxblack-8252-cfm-cpu-cooler-nh-d15-chromaxblack


SSD:
    You really want an M.2 Drive that supports The Gen4 PCIE interface.

    sabrent seems to be a good manufacter, not as confident as D15


MOBO:
    Best mobo manufactuers are: Asus, Asrock, Gigabyte, MSI

    One reviewer mentioned good customer service from: EVGA, Corsair, Logitech, NZXT and to a lesser extent MSI.
    One reviewer mentioned bad customer service from: Asus, Gigabyte, Powercolor, Asrock

    Asus ROG Strix X299-E Gaming II
    MSI X299 PRO


Cases:
    https://www.ranker.com/list/the-best-computer-case-manufacturers/computer-hardware

    Corsair, NZXT

    https://www.anandtech.com/show/7124/corsair-carbide-air-540-case-review/5

    Deep Silence 5 Full Tower E-ATX Case for Sensitive Audio Workstation and Storage Dense Applications, Black

    https://www.amazon.com/Lian-Li-LAN2MRW-Tempered-LANCOOL/dp/B08DX68X9W/ref=sr_1_1?dchild=1&keywords=Lian%2BLi%2BLancool%2BII%2BMesh&qid=1607712965&sr=8-1&th=1


Mid tower possibilities:

    Lian Li Lancool II Mesh

    Phanteks P500A Digital




Current Build:
    * EVGA T2 1000 W 80+ Titanium Certified Fully Modular ATX Power Supply


"""
import ubelt as ub
import slugify


def slugify_key(text):
    return slugify.slugify(text, separator='_', lowercase=True)


def varied_values(dict_list, min_variations=1):
    """
    Given a list of dictionaries, find the values that differ between them

    Args:
        dict_list (List[Dict]):
            The values of the dictionary must be hashable. Lists will be
            converted into tuples.

        min_variations (int, default=1): minimum number of variations to return

    TODO:
        - [ ] Is this a ubelt function?

    Example:
        >>> num_keys = 10
        >>> num_dicts = 10
        >>> all_keys = {ub.hash_data(i)[0:16] for i in range(num_keys)}
        >>> dict_list = [
        >>>     {key: ub.hash_data(key)[0:16] for key in all_keys}
        >>>     for _ in range(num_dicts)
        >>> ]
        >>> import random
        >>> rng = random.Random(0)
        >>> for data in dict_list:
        >>>     if rng.random() > 0.5:
        >>>         for key in list(data):
        >>>             if rng.random() > 0.9:
        >>>                 data[key] = rng.randint(1, 32)
        >>> varied = varied_values(dict_list)
        >>> print('varied = {}'.format(ub.repr2(varied, nl=1)))
    """
    all_keys = set()
    for data in dict_list:
        all_keys.update(data.keys())

    varied = ub.ddict(set)
    for data in dict_list:
        for key in all_keys:
            value = data.get(key, ub.NoParam)
            if isinstance(value, list):
                value = tuple(value)
            varied[key].add(value)

    for key, values in list(varied.items()):
        if len(values) <= min_variations:
            del varied[key]
    return varied


def motherboard_info():
    """
    REQUIRES SUDO

    xdoctest -m ~/misc/notes/buildapc.py motherboard_info
    """
    import re
    info = ub.cmd('sudo dmidecode -t 9')
    pcie_slots = []
    chunks = info['out'].split('\n\n')
    for chunk in chunks:
        item = {}
        for line in chunk.split('\n'):
            # doesn't get all data correctly (e.g. characteristics)
            parts = re.split('\t*:', line, maxsplit=1)
            if len(parts) == 2:
                key, val = parts
                key = key.strip()
                val = val.strip()
                if key in item:
                    raise KeyError(f'key={key} already exists')
                item[key] = val
        if item:
            item = ub.map_keys(slugify_key, item)
            pcie_slots.append(item)

    pcie_usage = ub.dict_hist(item['current_usage'] for item in pcie_slots)

    _varied = varied_values(pcie_slots, min_variations=0)
    _varied = ub.map_keys(slugify_key, _varied)
    unvaried = {k: ub.peek(v) for k, v in _varied.items() if len(v) == 1}
    varied = {k: v for k, v in _varied.items() if len(v) > 1}

    print(info['out'])

    # info = ub.cmd('sudo dmidecode -t baseboard')
    # print(info['out'])


def parse_cpu_info(percore=False):
    """
    Get a nice summary of CPU information

    Requirements:
        pip install python-slugify

    Ignore:
        cpu_info = parse_cpu_info()
        print(cpu_info['varied']['cpu_mhz'])
        print('cpu_info = {}'.format(ub.repr2(cpu_info, nl=3)))
    """
    import re
    info = ub.cmd('cat /proc/cpuinfo')
    cpu_lines = info['out'].split('\n\n')
    cores = []
    for lines in cpu_lines:
        core = {}
        for line in lines.split('\n'):
            parts = re.split('\t*:', line, maxsplit=1)
            if len(parts) == 2:
                key, val = parts
                key = key.strip()
                val = val.strip()
                if key in core:
                    raise KeyError(f'key={key} already exists')
                core[key] = val
        if len(core):
            core = ub.map_keys(slugify_key, core)
            cores.append(core)
    _varied = varied_values(cores, min_variations=0)
    unvaried = {k: ub.peek(v) for k, v in _varied.items() if len(v) == 1}
    varied = {k: v for k, v in _varied.items() if len(v) > 1}

    cpu_info = {
        'varied': varied,
        'unvaried': unvaried,
    }
    if percore:
        cpu_info['cores'] = cores
    return cpu_info


def current_specs():
    cpu_info = parse_cpu_info()
    cpu_info['unvaried']['model_name']


tiers = {
    'monstrous': 16,
    'extremist': 15,
    'enthusiast': 14,
    'exceptional': 13,
}


options = [

    {'type': 'case', 'name': 'Cosmos C700M', 'price': 500, 'tier': 'monstrous'},
    {'type': 'case', 'name': 'Enthoo Elite', 'price': 843, 'tier': 'monstrous'},
    {'type': 'case', 'name': 'Dark Base Pro 900', 'price': 260, 'tier': 'monstrous'},
    {'type': 'case', 'name': 'Enthoo Primo', 'price': 251, 'tier': 'enthusiast'},


    {'type': 'RAM', 'name': '64GB DDR4', 'price': 240, 'tier': 'monstrous'},
    {'type': 'RAM', 'name': '32GB DDR4', 'price': 128, 'tier': 'monstrous'},


    # {'type': 'CPU', 'name': 'Intel Core i9-109080XE', 'price': 969.99, 'TDP': '165 W', 'cores': 18, 'clock': '4.4 GHz' },
    {'type': 'CPU', 'name': 'Intel Core i9-9900KF', 'price': 399.99, 'TDP': '165 W', 'cores': 8, 'clock': '3.6 GHz'},


    {'type': 'SSD', 'name': 'Crucial P1 1TB PCIe SSD', 'price': 93.99, 'TDP': '7 W', 'size': '1TB'},


    {'type': 'Motherboard', 'name': 'MSI TRX40 PRO', 'price': 400, 'tier': 'monstrous'},
    {'type': 'Motherboard', 'name': 'ASUS TRX40-PRO', 'price': 400, 'tier': 'monstrous'},
    {'type': 'Motherboard', 'name': 'GIGABYTE TRX40 Pro', 'price': 399, 'tier': 'monstrous'},
]


def main():
    grouped = ub.group_items(options, lambda x: x['type'])

    build = {}

    for key, values in grouped.items():
        print('key = {!r}'.format(key))
        values = sorted(values, key=lambda x: x['price'])
        chosen = values[-1]
        print('chosen = {!r}'.format(chosen))
        build[key] = chosen

    print('build = {}'.format(ub.repr2(build, nl=2)))


def pole_mounts_comparison():
    """
    Found 2 good suppliers of pole workstations

    https://www.ergomart.com/monitor-mounts/mcart-heavy-duty-computer-monitor-carts-custom-mounting-system/rolling-monitor-cart-base-and-mounting-pole
    https://www.ergomart.com/ergonomic-accessories/cpu-holders/cpu-computer-tower-holder
    https://www.ergomart.com/monitor-mounts/monitor-arms/heavy-duty/saa2718-monitor-arm

    https://www.computerdesksdepot.com/collections/parts-for-exclusively-35-mm-pole-diameters

    https://www.computerdesksdepot.com/products/vc01-mc-cpu-holder-for-vc01-pole-computer-workstation?_pos=1&_sid=c5109caca&_ss=r

    https://www.computerdesksdepot.com/collections/parts-for-exclusively-35-mm-pole-diameters/products/dvc04-cpu-pole-cpu-holder-for-cuzzi-pole-carts-35-mm-poles
    https://www.computerdesksdepot.com/collections/5-pole-lcd-monitor-mounts/products/df17-arm-lcd-pole-arm-for-35-mm-diameter-poles
    https://www.computerdesksdepot.com/collections/accessories-parts/products/dvc03-sh-shelf-for-cuzzi-dvc-pole-carts-35-mm-pole-diameters
    """

    ergomart_options = [
        {'type': 'mobile_base', 'price': 238.53},
        {'type': 'pole', 'height': 5, 'price': 118.08},
        {'type': 'pole', 'height': 6, 'price': 137.53},
        # {'type': 'pole', 'height': 4, 'price': 99.09},
        {'type': 'cpu_holder', 'size': 'large', 'price': 71.66},
        {'type': 'cpu_holder', 'size': 'medium', 'price': 61.95},
        {'type': 'monitor_arm', 'size': '27hz', 'price': 236.69},
    ]

    groups = ub.group_items(ergomart_options, lambda x: x['type'])
    build = []
    for key, group in groups.items():
        cheap = sorted(group, key=lambda x: x['price'])[0]
        build.append(cheap)
    print('build = {}'.format(ub.repr2(build, nl=1)))
    total = sum(p['price'] for p in build)
    print('total = {!r}'.format(total))

    """
    Whole setup is ~50lb

    Arm itself is 5lb

    Pole is 25lb.


    https://www.computerdesksdepot.com/products/cuzzi-dpa-1-pole-clamp-for-pole-diam-1-00-1-25?_pos=1&_sid=1157c7a8e&_ss=r
    https://www.computerdesksdepot.com/collections/pole-mount-products-monitor-mounts-arms-keyboard-trays-shelves/products/vc01-mc-cpu-holder-for-vc01-pole-computer-workstation


    https://studiored.com/tip-point-calculator/
    https://physics.stackexchange.com/questions/244910/mass-required-to-prevent-sign-falling-over-with-a-set-wind-load-activity-stati

                2'


               |-----o 25lb
               |
         5'    |   x (center of mass)
               |
              === <- pivot


               2'

      25 lB

      Box + pole = 20 lb

      parts = [
          {'xy': (0, 0), 'weight': 6.0, 'name': 'base'},
          {'xy': (0, 2.5), 'weight': 10, 'name': 'pole'},
          {'xy': (1.42, 5), 'weight': 25, 'name': 'monitor'},
          {'xy': (1.42 / 2, 5), 'weight': 5, 'name': 'arm'},
      ]

      xy_pos = np.array([p['xy'] for p in parts])
      w = np.array([p['weight'] for p in parts])[:, None]

      # Crude approximation to calculate the center of mass.
      # The object will tip if the x-coordinate of the COM is
      # past the edge of the base (the pivot point)

      center_of_mass = (xy_pos * w).sum(axis=0) / w.sum(axis=0)
      print('center_of_mass = {!r}'.format(center_of_mass))

      # COM = 0.71, 2.72727273

      Base extends 1'

    """

    computerdesksdeop_options = [
        {'type': 'pole_and_base', 'price': 198.00, 'model': 'DVC04-BYO', 'height': '65"'},
        {'type': 'cpu_holder', 'size': 'medium', 'price': 65.00, 'model': ''},
        {'type': 'monitor_arm', 'size': '17', 'model': 'DF17ARM', 'price': 89.00, 'max_weight': '25 lb'},
        # {'type': 'monitor_arm', 'size': '17.5', 'model': 'DP170', 'price': 148.00, 'max_weight': '25 lb'},

        # DVC03-SH Shelf 40 lb 65.0
    ]
    groups = ub.group_items(computerdesksdeop_options, lambda x: x['type'])
    build = []
    for key, group in groups.items():
        cheap = sorted(group, key=lambda x: x['price'])[0]
        build.append(cheap)
    print('build = {}'.format(ub.repr2(build, nl=1)))
    total = sum(p['price'] for p in build)
    print('total = {!r}'.format(total))


def hdd_cost():
    # https://www.amazon.com/Seagate-BarraCuda-Computers-ST10000DM0004-Refurbished/dp/B07MWCVMXJ/ref=sr_1_4?dchild=1&keywords=barracuda+hdd&qid=1610773536&sr=8-4
    # https://www.amazon.com/Seagate-IronWolf-7200RPM-Internal-3-5-Inch/dp/B07H4VBRKW/ref=BDG-DBC__1?pd_rd_w=vg0S7&pf_rd_p=7cbca5e6-eb08-447b-a1bf-60db44887201&pf_rd_r=VN5X2948PZEXNVBD9TBN&pd_rd_r=38e6ddb7-9d78-4508-b17c-f593fbc4f957&pd_rd_wg=S1zOw&pd_rd_i=B07H4VBRKW&psc=1
    # https://www.newegg.com/seagate-exos-x10-st10000nm0096-10tb/p/1Z4-002P-00DU5?Item=9SIA994C784701&Description=seagate&cm_re=seagate-_-1Z4-002P-00DU5-_-Product
    candidates = [
        {'cost': 198.65, 'TB': 10, 'RPM': 7200, 'sale': True, 'condition': 'refurbished', 'line': 'baraccuda compute'},
        {'cost': 248.99, 'TB': 10, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'iron wolf'},
        {'cost': 249.99, 'TB': 10, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'ironwolf'},

        {'cost': 162.99, 'TB': 6, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'ironwolf'},
        {'cost': 139.99, 'TB': 6, 'RPM': 5400, 'sale': True, 'condition': 'new', 'line': 'baraccuda compute'},
        {'cost': 154.99, 'TB': 8, 'RPM': 5400, 'sale': True, 'condition': 'new', 'line': 'baraccuda compute'},
        {'cost': 340.00, 'TB': 8, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'baraccuda compute pro'},
        {'cost': 199.99, 'TB': 8, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'ironwolf'},
        {'cost': 252.99, 'TB': 12, 'RPM': 7200, 'sale': False, 'condition': 'refurbished', 'line': 'ironwolf'},
        {'cost': 435.04, 'TB': 14, 'RPM': None, 'sale': False, 'condition': 'new', 'line': 'ironwolf'},
        # {'cost': 101.50, 'TB': 2, 'RPM': 7200, 'sale': True},

        {'cost': 198.99, 'TB': 10, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'exos'},
        {'cost': 299.99, 'TB': 12, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'exos'},
        {'cost': 209.99, 'TB': 10, 'RPM': 7200, 'sale': False, 'condition': 'refurbished', 'line': 'exos'},


        {'cost': 421.99, 'TB': 16, 'RPM': 7200, 'sale': True, 'condition': 'new', 'line': 'skyhawk-ai', 'date': '2021-07-10'},
        {'cost': 356.99, 'TB': 12, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'skyhawk-ai', 'date': '2021-07-10'},

        {'cost': 399.06, 'TB': 12, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'ironwolf-pro', 'date': '2021-07-10'},
        {'cost': 359.06, 'TB': 12, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'ironwolf', 'date': '2021-07-10'},

        {'cost': 299.99, 'TB': 10, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'ironwolf', 'date': '2021-07-10'},
        {'cost': 390.00, 'TB': 10, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'baracuda-compute-pro', 'date': '2021-07-10'},

        {'cost': 1120, 'TB': 40, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'ironwolf-pro-x4', 'date': '2021-07-10', 'seller': 'B&H'},
        {'cost': 260, 'TB': 10, 'RPM': 7200, 'sale': False, 'condition': 'new', 'line': 'skyhawk', 'date': '2021-07-10', 'seller': 'B&H'},
    ]


    # https://www.seagate.com/products/nas-drives/ironwolf-hard-drive/
    # https://www.adorama.com/l/Computers/Drives-comma-SSD-and-Storage/Seagate~Hard-Disk-Drives?sel=Capacity_10TB
    seagate_msrps = [
        {'cost': 146, 'TB': 4, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 209, 'TB': 6, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 289, 'TB': 8, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 356, 'TB': 10, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': 'air', 'date': '2021-07-10'},
        {'cost': 356, 'TB': 10, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': 'helium', 'date': '2021-07-10'},
        {'cost': 430, 'TB': 12, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 503, 'TB': 14, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 577, 'TB': 16, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},
        {'cost': 656, 'TB': 18, 'RPM': 7200, 'line': 'ironwolf-pro', 'design': None, 'date': '2021-07-10'},

        {'cost': 241, 'TB':  8, 'RPM': 7200, 'line': 'ironwolf', 'design': None, 'date': '2021-07-10'},
        {'cost': 314, 'TB': 10, 'RPM': 7200, 'line': 'ironwolf', 'design': None, 'date': '2021-07-10'},
        {'cost': 377, 'TB': 12, 'RPM': 7200, 'line': 'ironwolf', 'design': None, 'date': '2021-07-10'},

        {'cost': 293, 'TB': 10, 'RPM': 7200, 'line': 'skyhawk-ai', 'design': None, 'date': '2021-07-10'},
        {'cost': 356, 'TB': 12, 'RPM': 7200, 'line': 'skyhawk-ai', 'design': None, 'date': '2021-07-10'},
        {'cost': 472, 'TB': 16, 'RPM': 7200, 'line': 'skyhawk-ai', 'design': None, 'date': '2021-07-10'},
        {'cost': 524, 'TB': 18, 'RPM': 7200, 'line': 'skyhawk-ai', 'design': None, 'date': '2021-07-10'},

        {'cost': 230, 'TB': 10, 'RPM': 7200, 'line': 'skyhawk', 'design': None, 'date': '2021-07-10'},
    ]

    candidates = seagate_msrps
    for cand in candidates:
        cand['cost_per_TB'] = cand['cost'] / cand['TB']

    import pandas as pd
    df = pd.DataFrame(candidates)
    df = df.sort_values('cost_per_TB')
    print(df)


    print('candidates = {}'.format(ub.repr2(candidates, nl=1, precision=2, align=':')))


considering = ub.codeblock(
    '''
    https://www.lg.com/us/monitors/lg-27UK650-W-4k-uhd-led-monitor#

    https://www.lg.com/us/monitors/lg-27GL850-B-gaming-monitor

    https://www.amazon.com/Dell-U2720QM-UltraSharp-Ultra-Thin-DisplayPort/dp/B08F5J8S6Y?ref_=ast_sto_dp


    https://www.amazon.com/Dell-U2720QM-UltraSharp-Ultra-Thin-DisplayPort/dp/B08F5J8S6Y?ref_=ast_sto_dp

    # Has 2560x1440 resolution, which is what I like anyway
    #
    https://www.amazon.com/LG-27GL83A-B-Ultragear-Compatible-Monitor/dp/B07YGZL8XF/ref=sr_1_2_sspa?dchild=1&keywords=4k+monitor&qid=1619557709&sr=8-2-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzNjBXRVNRRkNMWU5QJmVuY3J5cHRlZElkPUEwMDgxNzQ4MUQ3RE9SM0dTTkkyTCZlbmNyeXB0ZWRBZElkPUEwNTM2NTc0MTE5SVJJVzQySjJGQyZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU=

    WQHD
    ''')
