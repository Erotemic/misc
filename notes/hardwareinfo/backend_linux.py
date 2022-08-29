"""
https://www.reddit.com/r/linux/comments/n1501j/linux_performance_tools/

SeeAlso:
    ~/code/erotemic/pub/owned_hardware.py
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
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/notes'))
        >>> from hardwareinfo.backend_linux import *  # NOQA
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

    # pcie_usage = ub.dict_hist(item['current_usage'] for item in pcie_slots)

    _varied = varied_values(pcie_slots, min_variations=0)
    _varied = ub.map_keys(slugify_key, _varied)
    # unvaried = {k: ub.peek(v) for k, v in _varied.items() if len(v) == 1}
    # varied = {k: v for k, v in _varied.items() if len(v) > 1}

    print(info['out'])

    # info = ub.cmd('sudo dmidecode -t baseboard')
    # print(info['out'])


def ram_info():
    info = ub.cmd('sudo dmidecode --type 17')
    print(info['out'])


def parse_cpu_info(percore=False):
    """
    Get a nice summary of CPU information

    Requirements:
        pip install python-slugify

    Ignore:
        cpu_info = parse_cpu_info()
        print(cpu_info['varied']['cpu_mhz'])
        print('cpu_info = {}'.format(ub.repr2(cpu_info, nl=3)))

    Notes:
        * lscpu
    """
    # ALSO
    import cpuinfo
    cpu_info = cpuinfo.get_cpu_info()

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


def lspci():
    """
    list all PCI devices

    lspci is a utility for displaying information about PCI buses in the system
    and devices connected to them.

    References:
        https://diego.assencio.com/?index=649b7a71b35fc7ad41e03b6d0e825f07

    Returns:
        List[Dict]: each dict is an item that contains keys:
            'Slot', 'Class', 'Vendor', 'Device', 'SVendor', 'SDevice', 'Rev'

    Example:
        items = lspci()
        [item['Class'] for item in items]
    """
    import re
    info = ub.cmd('lspci -vmm')
    parts = re.split('\n *\n', info['out'])
    items = []
    for part in parts:
        part = part.strip()
        if part:
            item = dict([line.split(':\t') for line in part.split('\n')])
            items.append(item)
    return items


def parse_gpu_info():
    """
    https://www.cyberciti.biz/faq/linux-tell-which-graphicsovga-card-installed/
    """
    gpus = []
    for item in lspci():
        if item['Class'] == 'VGA compatible controller':
            gpus.append(item)
    return gpus


def printer_info():
    """
    Notes:
        lpstat -p
    """
    return ub.cmd('lpstat -p')['out']


def diskinfo():
    """
    sudo lshw -class disk

    lsblk --scsi --output NAME,KNAME,LABEL,MOUNTPOINT,UUID,PARTTYPE,PARTUUID,MODEL,TYPE,SIZE,STATE
    lsblk --scsi --output NAME,KNAME,LABEL,SERIAL,UUID,PARTTYPE,PARTUUID,MODEL,TYPE,SIZE,STATE --json
    """
    import json
    if 0:
        helpstr = ub.cmd('lsblk --help')['out'].split('Available output columns:')[1]
        parsing = [line.strip().partition(' ') for line in helpstr.strip().split('\n')[1:-2]]
        coldesc = {p[0].strip().lower(): p[-1].strip() for p in parsing}
        print('coldesc = {}'.format(ub.repr2(coldesc, nl=1, sort=0)))
    coldesc = {
        'kname': 'internal kernel device name',
        'path': 'path to the device node',
        'maj:min': 'major:minor device number',
        'fsavail': 'filesystem size available',
        'fssize': 'filesystem size',
        'fstype': 'filesystem type',
        'fsused': 'filesystem size used',
        'fsuse%': 'filesystem use percentage',
        'fsroots': 'mounted filesystem roots',
        'fsver': 'filesystem version',
        'mountpoint': 'where the device is mounted',
        'mountpoints': 'all locations where device is mounted',
        'label': 'filesystem LABEL',
        'uuid': 'filesystem UUID',
        'ptuuid': 'partition table identifier (usually UUID)',
        'pttype': 'partition table type',
        'parttype': 'partition type code or UUID',
        'parttypename': 'partition type name',
        'partlabel': 'partition LABEL',
        'partuuid': 'partition UUID',
        'partflags': 'partition flags',
        'ra': 'read-ahead of the device',
        'ro': 'read-only device',
        'rm': 'removable device',
        'hotplug': 'removable or hotplug device (usb, pcmcia, ...)',
        'model': 'device identifier',
        'serial': 'disk serial number',
        'size': 'size of the device',
        'state': 'state of the device',
        'owner': 'user name',
        'group': 'group name',
        'mode': 'device node permissions',
        'alignment': 'alignment offset',
        'min-io': 'minimum I/O size',
        'opt-io': 'optimal I/O size',
        'phy-sec': 'physical sector size',
        'log-sec': 'logical sector size',
        'rota': 'rotational device',
        'sched': 'I/O scheduler name',
        'rq-size': 'request queue size',
        'type': 'device type',
        'disc-aln': 'discard alignment offset',
        'disc-gran': 'discard granularity',
        'disc-max': 'discard max bytes',
        'disc-zero': 'discard zeroes data',
        'wsame': 'write same max bytes',
        'wwn': 'unique storage identifier',
        'rand': 'adds randomness',
        'pkname': 'internal parent kernel device name',
        'hctl': 'Host:Channel:Target:Lun for SCSI',
        'tran': 'device transport type',
        'subsystems': 'de-duplicated chain of subsystems',
        'rev': 'device revision',
        'vendor': 'device vendor',
        'zoned': 'zone model',
        'dax': 'dax-capable device',
    }
    colnames = list(coldesc.keys())
    out = ub.cmd(f'lsblk --all --json --output={",".join(colnames)}')['out']
    data = json.loads(out)
    cols = ['kname', 'model', 'serial', 'size', 'type']
    import pandas as pd
    df = pd.DataFrame(data['blockdevices'])
    df = df[df['type'] == 'disk']
    print(df[cols])


# def current_specs():
#     cpu_info = parse_cpu_info()
#     cpu_info['unvaried']['model_name']
