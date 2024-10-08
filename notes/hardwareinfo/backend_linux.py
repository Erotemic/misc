"""

Requirements:
    pip install python-slugify


References:
    https://opensource.com/article/19/9/linux-commands-hardware-information
    https://www.reddit.com/r/linux/comments/n1501j/linux_performance_tools/


SeeAlso:
    ~/code/erotemic/pub/owned_hardware.py
"""
import ubelt as ub


def slugify_key(text):
    import slugify
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
    from collections import defaultdict
    NoParam = object()
    all_keys = set()
    for data in dict_list:
        all_keys.update(data.keys())
    varied = defaultdict(set)
    for data in dict_list:
        for key in all_keys:
            value = data.get(key, NoParam)
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

    xdoctest -m ~/misc/notes/hardwareinfo/backend_linux.py motherboard_info

    SeeAlso:
        https://askubuntu.com/questions/179958/how-do-i-find-out-my-motherboard-model
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

    # _varied = varied_values(pcie_slots, min_variations=0)
    # _varied = ub.map_keys(slugify_key, _varied)
    # unvaried = {k: ub.peek(v) for k, v in _varied.items() if len(v) == 1}
    # varied = {k: v for k, v in _varied.items() if len(v) > 1}

    print(info['out'])

    import pandas as pd
    df = pd.DataFrame(pcie_slots)
    import rich
    rich.print(df.to_string())

    # info = ub.cmd('sudo dmidecode -t baseboard')
    # print(info['out'])

    ## Get mootherboard serial
    info = ub.cmd('sudo dmidecode -t 2')
    print(info['out'])


def ram_info():
    """
    xdoctest ~/misc/notes/hardwareinfo/backend_linux.py ram_info
    """
    import re
    info = ub.cmd('sudo dmidecode --type 17')
    print(info['out'])
    dmi_entries = []
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
            dmi_entries.append(item)

    num_empty = 0
    total_bytes = 0
    ram_sizestrs = []
    filled_entries = []
    for entry in dmi_entries:
        sizestr = entry.get('size', 'error')
        if 'no module' in sizestr.lower():
            num_empty += 1
        else:
            filled_entries.append(entry)
            mag, unit = sizestr.split(' ')
            if sizestr.endswith('MB'):
                total_bytes += int(mag) * 2 ** 20
            elif sizestr.endswith('GB'):
                total_bytes += int(mag) * 2 ** 30
            else:
                raise NotImplementedError
            ram_sizestrs.append(sizestr)

    try:
        import pandas as pd
        df = pd.DataFrame(filled_entries)
        import rich
        rich.print(df.T.to_string())
    except Exception:
        ...

    total_gb = total_bytes / (2 ** 30)

    print(ub.dict_hist(ram_sizestrs))
    num_slots = len(dmi_entries)
    print(f'Total RAM size: {total_gb} GB')
    print(f'Number of RAM slots: {num_slots}')
    print(f'Number of empty slots: {num_empty}')
    print(f'Installed slot sizes: {ram_sizestrs}')


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
    import subprocess
    stdout = subprocess.check_output(['cat', '/proc/cpuinfo'],
                                     universal_newlines=True)
    cpu_lines = stdout.split('\n\n')
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
            # core = {slugify_key(k): v for k, v in core.items()}
            cores.append(core)
    _varied = varied_values(cores, min_variations=0)
    unvaried = {k: next(iter(v)) for k, v in _varied.items() if len(v) == 1}
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

    References:
        https://askubuntu.com/questions/609708/how-to-find-hard-drive-brand-name-or-model

    Note:
        A lot of disk info commands require sudo

        udisksctl  status
        udisksctl info -b /dev/sda1
        udisksctl info -b /dev/nvme1n1



        udevadm info --query=all --name=/dev/sda1
        udevadm info --query=all --name=/dev/nvme1n1
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
    # colnames = list(coldesc.keys())
    # out = ub.cmd(f'lsblk --all --json --output={",".join(colnames)}')['out']
    out = ub.cmd('lsblk --all --json')['out']
    data = json.loads(out)
    # cols = ['kname', 'model', 'serial', 'size', 'type']
    import pandas as pd
    df = pd.DataFrame(data['blockdevices'])
    df = df[df['type'] == 'disk']
    # print(df[cols])


def network_connector_speed():
    """
    ethernet speed

    References:
        https://serverfault.com/questions/207474/how-do-i-verify-the-speed-of-my-nic
        https://phoenixnap.com/kb/linux-network-speed-test

    Notes:
        sudo ethtool eno1 | grep Speed
        sudo ethtool enp7s0 | grep Speed
        sudo ethtool wlp8s0 | grep Speed

        # To monitor speeds
        sudo apt install cbm

        # Speedtest on the CLI
        pip install speedtest-cli


    """


def monitor_info():
    """
    Get information about connected monitors / displays

    Looks like the information isn't that good.

    References:
        https://askubuntu.com/questions/371261/display-monitor-info-via-command-line

    Notes:
        sudo apt-get install read-edid

        sudo get-edid | parse-edid

        lshw -c display

        xrandr --prop

        dbus-send --session --print-reply --dest=org.gnome.Mutter.DisplayConfig /org/gnome/Mutter/DisplayConfig org.gnome.Mutter.DisplayConfig.GetCurrentState

    """
    info = ub.cmd('xrandr --prop')
    print(info.stdout)


def monitor_psu_voltage():
    r"""
    Seems that a multimeter is the most reliable way to do this, but there does
    seem to be some software support.

    sensors-detect


    References:
        https://askubuntu.com/questions/1009423/find-the-power-supply-hardware-information-for-a-pc-using-ubuntus-command-line

    sudo apt-get install conky-all


    Steps I took:

        I ran

        sudo sensors-detect

        said yes to everything

        it asked me to add

        coretemp
        nct6775

        to my kernel modules in /etc/modules


        To check if they existed I found:

        https://askubuntu.com/questions/181433/how-can-i-find-out-what-drivers-are-built-into-my-kernel

        cat /boot/config-`uname -r`
        grep "=y" /boot/config-`uname -r`

        grep "=y" /boot/config-`uname -r` | grep core -i

        find /usr /lib /opt -type d -name modules -exec find {} -path "*`uname -r`*" -name "*.ko" \;


        # To find all non-built in modules:
        find /lib/modules/`uname -r` | grep -oP "(?<=/)\w+(?=\.ko)"

        find /lib/modules/`uname -r` | grep -oP "(?<=/)\w+(?=\.ko)" | grep coretemp
        find /lib/modules/`uname -r` | grep -oP "(?<=/)\w+(?=\.ko)" | grep nct6775

        locate coretemp.ko
        locate nct6775.ko

    """


# def current_specs():
#     cpu_info = parse_cpu_info()
#     cpu_info['unvaried']['model_name']
if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/hardwareinfo/backend_linux.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
