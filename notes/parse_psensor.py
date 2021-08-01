"""
TODO:
    - [ ] http://manpages.ubuntu.com/manpages/bionic/man1/psensor-server.1.html
"""
import ubelt as ub


def read_psensor_log():
    fpath = ub.expandpath('~/.psensor/sensors.log')

    with open(fpath) as file:
        text = file.read()

    sessions = []
    session = []
    for line in text.split('\n'):
        if line.startswith('I'):
            if session:
                sessions.append(session)
            session = [line]
        else:
            session.append(line)


    session_dfs = []
    import datetime
    for session in sessions:
        columns = []
        rows = []
        init_line = None
        # init_info = None
        base_timestamp = 0
        for line in session:
            if line:
                if line.startswith('I'):
                    init_line = line
                    parts = init_line.split(',')
                    base_timestamp = int(parts[1])
                    # init_info = {
                    #     'type': parts[0],
                    #     'unix_timestamp': base_timestamp,
                    #     'iso_timestamp': datetime.datetime.utcfromtimestamp(base_timestamp).isoformat(),
                    #     'version': parts[2],
                    # }

                elif line.startswith('S'):
                    parts = line.split(',')
                    info = {
                        'type': parts[0],
                        'name': parts[1],
                        '???': parts[2],
                    }
                    columns.append(info['name'])
                else:
                    parts = line.split(',')
                    time, *measures = parts
                    measures = [float(m) if m.strip() else float('nan')
                                for m in measures]
                    raw = ub.dzip(columns, measures)

                    # nice = ub.dict_diff(raw, drop)
                    # nice = ub.map_keys(mapper, nice)

                    uptime = int(time)
                    unix_timestamp = base_timestamp + uptime
                    utc_time = datetime.datetime.utcfromtimestamp(unix_timestamp)

                    for key, val in raw.items():
                        row = {'temp': val, 'device': key}
                        # row['datetime'] = utc_time.isoformat()
                        row['datetime'] = utc_time
                        row['unix_timestamp'] = unix_timestamp
                        row['uptime'] = uptime
                        rows.append(row)

        import pandas as pd
        session_df = pd.DataFrame(rows)
        session_dfs.append(session_df)

    all_df = pd.concat(session_dfs, ignore_index=True)
    return all_df


def main():

    cpus = [
        'lmsensor coretemp-isa-0000 Core 0',
        'lmsensor coretemp-isa-0000 Core 1',
        'lmsensor coretemp-isa-0000 Core 2',
        'lmsensor coretemp-isa-0000 Core 3',
        'lmsensor coretemp-isa-0000 Core 4',
        'lmsensor coretemp-isa-0000 Core 5',
        'lmsensor coretemp-isa-0000 Core 6',
        'lmsensor coretemp-isa-0000 Core 7',
    ]

    alias = {
        '3090': 'nvctrl GeForce GTX 1080 Ti 1 temp',
        'cpu': 'lmsensor coretemp-isa-0000 Package id 0',
        '1080ti': 'nvctrl GeForce RTX 3090 0 temp',
    }

    drop = [
        'lmsensor acpitz-acpi-0 temp1',
        'lmsensor nvme-pci-0200 Composite',
        'nvctrl GeForce RTX 3090 0 graphics', 'nvctrl GeForce RTX 3090 0 video',
        'nvctrl GeForce RTX 3090 0 memory', 'nvctrl GeForce RTX 3090 0 PCIe',
        'nvctrl GeForce GTX 1080 Ti 1 graphics',
        'nvctrl GeForce GTX 1080 Ti 1 video',
        'nvctrl GeForce GTX 1080 Ti 1 memory',
        'nvctrl GeForce GTX 1080 Ti 1 PCIe', 'nvctrl NVIDIA 0 fan rpm',
        'nvctrl NVIDIA 0 fan level', 'nvctrl NVIDIA 1 fan rpm',
        'nvctrl NVIDIA 1 fan level', 'nvctrl NVIDIA 2 fan rpm',
        'nvctrl NVIDIA 2 fan level', 'gtop2 cpu usage', 'gtop2 mem free',
        'udisks2 ST10000DM0004-1ZC101-ZA29QHSG',
        'udisks2 ST10000DM0004-1ZC101-ZA2215HL',
        'udisks2 ST10000DM0004-1ZC101-ZA22W366',
        'udisks2 ST10000DM0004-1ZC101-ZA22SPLG'
    ]
    mapper = ub.dict_union(ub.invert_dict(alias), {c: ''.join(c.split(' ')[-2:]) for c in cpus})

    all_df = read_psensor_log()
    all_df['device'] = all_df['device'].apply(lambda x: mapper.get(x, None))
    all_df = all_df[all_df['device'].apply(lambda x: x is not None)]

    import datetime
    delta = datetime.timedelta(hours=72)
    min_time = datetime.datetime.now() - delta
    is_recent = all_df.datetime > min_time
    recent_df = all_df[is_recent]


    pivtbl = all_df.pivot('unix_timestamp', 'device', 'temp')

    import kwplot
    sns = kwplot.autosns()

    # from matplotlib.dates import date2num
    # all_df['date_ord'] = all_df['datetime'].map(lambda a: date2num(a))

    # sns.lineplot(data=pt)
    sns.lineplot(data=recent_df, x='unix_timestamp', y='temp', hue='device')
    sns.regplot(data=recent_df, x='unix_timestamp', y='temp', hue='device')
    sns.regplot
