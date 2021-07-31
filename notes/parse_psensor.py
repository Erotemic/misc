"""
TODO:
    - [ ] http://manpages.ubuntu.com/manpages/bionic/man1/psensor-server.1.html
"""
import ubelt as ub

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


session_dfs = []
for session in sessions:
    import datetime
    columns = []
    column_info = {}
    rows = []
    init_line = None
    init_info = None
    base_timestamp = 0
    for line in session:
        if line:
            if line.startswith('I'):
                init_line = line
                parts = init_line.split(',')
                base_timestamp = int(parts[1])
                init_info = {
                    'type': parts[0],
                    'timestamp': base_timestamp,
                    'iso_timestamp': datetime.datetime.utcfromtimestamp(base_timestamp).isoformat(),
                    'version': parts[2],
                }

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
                raw = ub.dzip(columns, [float(m) if m.strip() else float('nan') for m in measures])
                nice = ub.dict_diff(raw, drop)
                nice = ub.map_keys(mapper, nice)

                uptime = int(time)
                timestamp = base_timestamp + uptime
                utc_time = datetime.datetime.utcfromtimestamp(timestamp)

                for key, val in nice.items():
                    row = {'temp': val, 'device': key}
                    # row['datetime'] = utc_time.isoformat()
                    row['datetime'] = utc_time
                    row['timestamp'] = timestamp
                    row['uptime'] = uptime
                    rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    session_dfs.append(df)


all_df = pd.concat(session_dfs, ignore_index=True)
pt = all_df.pivot('timestamp', 'device', 'temp')


import kwplot
sns = kwplot.autosns()

sns.lineplot(data=pt)
sns.lineplot(data=all_df, x='datetime', y='temp', hue='device')
