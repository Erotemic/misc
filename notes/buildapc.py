
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
