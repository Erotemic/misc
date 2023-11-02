"""
https://github.com/Erotemic/py-SMART/tree/dev/sudo_in_smartctl
pip install pySMART

pip install git+https://github.com/truenas/py-SMART


Requirements:
    pySMART
    sudo apt-get install smartmontools


Each drive manufacturer defines a set of attributes,[21][22] and sets threshold values beyond which attributes should not pass under normal operation.

Each attribute has a raw value that can be a decimal or a hexadecimal value, whose meaning is entirely up to
  the drive manufacturer (but often corresponds to counts or a physical unit, such as degrees Celsius or
  seconds),

* a normalized value, which ranges from 1 to 253 (with 1 representing the worst case and 253 representing the best)

* a worst value, which represents the lowest recorded normalized value.

The initial default value of attributes is 100 but can vary between manufacturer


PCIE Lane Speeds
                              Lanes (GB/s)

        |          |          |          |          |          |
--------+         -+         -+         -+         -+         -+
Version |    x1    |    x2    |    x4    |    x8    |    x16   |
--------+         -+         -+         -+         -+         -+
    1.0 |  0.250   |
--------+         -+         -+         -+         -+         -+
    2.0 |  0.500   |  1.000   |  2.000   |  4.000   |  8.000   |
--------+         -+         -+         -+         -+         -+
    3.0 |  0.985   |
--------+         -+
    4.0 |  1.968   |
--------+         -+
    5.0 |  3.938   |
--------+         -+         -+         -+         -+         -+


Theoretical SATA Speed:
    750MB/S


Theoretical Disk IO Speeds:

                       Read         |    Write
    HDD - SATA     -      80 MB/s   |      160 MB/s
    SSD - SATA     - 500-600 MB/s
    SSD - PCIe 2.0 - 1000 MB/s (2 lanes)

    Refernces:
        https://en.wikipedia.org/wiki/PCI_Express


"""


def smart_table():
    import pandas as pd
    from pySMART import SMARTCTL
    from pySMART import DeviceList
    import ubelt as ub
    SMARTCTL.sudo = True

    devices = DeviceList()

    attr_rows = []
    dev_rows = []
    test_rows = []
    testcap_rows = []
    diag_rows = []
    msg_rows = []

    for dev in devices:
        devstate = ub.udict(dev.__getstate__(all_info=True))
        devrow = devstate - {'attributes', 'test_capabilities', 'tests', 'diagnostics', 'messages'}
        dev_rows.append(devrow)

        testcap_row = dev.test_capabilities
        testcap_row['dev'] = dev.name
        testcap_rows.append(testcap_row)

        diag_row = dev.diagnostics.__getstate__()
        diag_row['dev'] = dev.name
        diag_rows.append(diag_row)

        for test in dev.tests:
            row = {'dev': dev.name}
            row.update(test.__getstate__())
            test_rows.append(row)

        for msg in dev.messages:
            msg_rows.append({
                'dev': dev.name,
                'msg': msg,
            })

        for attr in dev.attributes:
            if attr is not None:
                row = {'dev': dev.name}
                row.update(attr.__getstate__())
                row['name'] = attr.name
                row['thresh'] = row.pop('threshold')
                attr_rows.append(row)

    dev_table = pd.DataFrame(dev_rows)
    test_df = pd.DataFrame(test_rows)
    msg_df = pd.DataFrame(msg_rows)
    testcap_df = pd.DataFrame(testcap_rows)
    attr_columns = ['dev', 'num', 'name', 'value', 'worst', 'thresh', 'type', 'updated', 'when_failed', 'raw']
    attrs_df = pd.DataFrame(attr_rows, columns=attr_columns)

    from rich import print
    print('')
    print('[green] --- Devices ---')
    print(dev_table.to_string())
    print('')
    print('[green] --- Device Test Capabilities ---')
    print(testcap_df.to_string())
    print('')
    print('[green] --- Device Tests ---')
    print(test_df.to_string())
    print('')
    print('[green] --- Device Messages ---')
    print(msg_df.to_string())
    print('')
    print('[green] --- Device Attributes ---')

    big_table = attrs_df.set_index(['name', 'num', 'dev']).sort_values(['num', 'name', 'dev'])
    print(big_table.to_string())

    for _, group in attrs_df.groupby(['num', 'name']):
        # print(group.to_string())
        value_failed = group['value'].astype(int) < group['thresh'].astype(int)
        worst_failed = group['worst'].astype(int) < group['thresh'].astype(int)
        any_failed = worst_failed | value_failed
        if any_failed.any():
            print('[red] !!! ATTENTION REQUIRED !!!')
            print(any_failed)

    devs = DeviceList()
    for dev in devs.devices:
        pass


def fio_test():
    """
    sudo apt install fio
    /usr/bin/fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=4G --readwrite=randrw --rwmixread=75

    https://docs.rocketpool.net/guides/node/local/prepare-pi.html#mounting-and-enabling-automount

    What you care about are the lines starting with read: and write: under the test: line.

    Your read should have IOPS of at least 15k and bandwidth (BW) of at least 60 MiB/s.
    Your write should have IOPS of at least 5000 and bandwidth of at least 20 MiB/s.

    """
    # file_system_infos = []
    # dpaths = []  # from file_system_infos
    import ubelt as ub
    dpaths = [
        (ub.Path.home() / 'tmp').ensuredir(),
        # ub.Path('/media/joncrall/flash1/tmp').mkdir(exist_ok=True) or ub.Path('/media/joncrall/flash1/tmp'),
        # ub.Path('/data/tmp').ensuredir(),
        ub.Path('/mnt/ramdisk/')
    ]
    jobs = ub.JobPool(mode='thread', max_workers=0)

    """

    /usr/bin/fio --randrepeat=1 --ioengine=libaio --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=4G --readwrite=randrw --rwmixread=75

    """

    command = '/usr/bin/fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=4G --readwrite=randrw --rwmixread=75'
    outs = {}
    for dpath in dpaths:
        job = jobs.submit(ub.cmd, command, cwd=dpath, verbose=2)
        job.dpath = dpath
    for job in jobs.as_completed(desc='collect jobs'):
        outs[job.dpath] = job.result()

        import parse
        pat = ub.codeblock(
            '''
            test: {gnum}: {opts}
            {fio_version}
            {logs}

            test: {grop_info}: {test_info}
              read: {READ_IOPS}, {READ_INFO}
               bw {rbwunit}: {read_bw}
               iops        : {read_iops}
              write: {WRITE_IOPS}, {WRITE_INFO}
               bw {wbwunit}: {write_bw}
               iops        : {write_iops}
              cpu          : {cpu}
              IO depths    : {depths}
                 submit    : {submit}
                 complete  : {complete}
                 issued rwts: {issued_rwts}
                 latency   : {latency}

            Run status {group_run_status_info}:
               READ: {READ_STAT}
              WRITE: {WRITE_STAT}
            ''')
        parser = parse.Parser(pat)

        rows = []
        for dpath, info in outs.items():
            out = info['out'].strip()
            print('')
            print(info['out'])
            print('')

            result = parser.parse(out)
            result.named['READ_INFO'].split(' ')
            result.named['READ_IOPS'].split(' ')
            write_iops = result.named['WRITE_IOPS'].split('=')[1]
            read_iops = result.named['READ_IOPS'].split('=')[1]

            row = {
                'r_iops': read_iops,
                'r_bw': result.named['READ_STAT'].split(',')[0].split('=')[1].split(' ')[0],
                'w_iops': write_iops,
                'w_bw': result.named['WRITE_STAT'].split(',')[0].split('=')[1].split(' ')[0],
                'dpath': dpath,
            }
            rows.append(row)
        import pandas as pd
        df = pd.DataFrame(rows)
        import rich
        rich.print(df.to_string())

        target = {
            'r_iops': '15.0k',
            'r_bw':  '60.0MiB/s',
            'w_iops': '5000',
            'w_bw':  '20.0MiB/s',
        }
        print('target')
        rich.print(pd.DataFrame([target]))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/notes/hardwareinfo/debug_disk.py smart_table
        python ~/misc/notes/hardwareinfo/debug_disk.py fio_test
        python ~/misc/notes/hardwareinfo/debug_disk.py fio_test
    """
    import fire
    fire.Fire()
