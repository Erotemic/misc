"""
https://github.com/Erotemic/py-SMART/tree/dev/sudo_in_smartctl
pip install pySMART


Each drive manufacturer defines a set of attributes,[21][22] and sets threshold values beyond which attributes should not pass under normal operation.

Each attribute has a raw value that can be a decimal or a hexadecimal value, whose meaning is entirely up to
  the drive manufacturer (but often corresponds to counts or a physical unit, such as degrees Celsius or
  seconds),

* a normalized value, which ranges from 1 to 253 (with 1 representing the worst case and 253 representing the best)

* a worst value, which represents the lowest recorded normalized value.

The initial default value of attributes is 100 but can vary between manufacturer """


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
    for _, group in attrs_df.groupby(['num', 'name']):
        print(group.to_string())
        value_failed = group['value'].astype(int) < group['thresh'].astype(int)
        worst_failed = group['worst'].astype(int) < group['thresh'].astype(int)
        any_failed = worst_failed | value_failed
        if any_failed.any():
            print('[red] !!! ATTENTION REQUIRED !!!')
            print(any_failed)

    devs = DeviceList()
    for dev in devs.devices:
        pass
