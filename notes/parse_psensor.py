"""
TODO:
    - [ ] http://manpages.ubuntu.com/manpages/bionic/man1/psensor-server.1.html
"""
import ubelt as ub
import datetime
import pandas as pd


def read_psensor_log():
    # Info about how data is formated
    # https://github.com/chinf/psensor/blob/4270c903e8007017b80c6c817dd41cf699f00df1/src/lib/slog.c
    fpath = ub.expandpath('~/.psensor/sensors.log')

    with open(fpath) as file:
        text = file.read()

    all_sessions_lines = []
    session_lines = []
    for line in text.split('\n'):
        if line:
            if line.startswith('I'):
                if session_lines:
                    all_sessions_lines.append(session_lines)
                session_lines = [line]
            else:
                session_lines.append(line)
    # finalize last accumulator
    if session_lines:
        all_sessions_lines.append(session_lines)

    session_dfs = []
    session_init_infos = []
    for session_x, session_lines in enumerate(all_sessions_lines):
        columns = []
        rows = []
        init_line = None
        # init_info = None
        base_timestamp = 0
        for line in session_lines:
            if line:
                if line.startswith('I'):
                    init_line = line
                    parts = init_line.split(',')
                    base_timestamp = int(parts[1])
                    init_info = {
                        'type': parts[0],
                        'unix_timestamp': base_timestamp,
                        'iso_timestamp': datetime.datetime.fromtimestamp(base_timestamp).isoformat(),
                        'version': parts[2],
                    }
                    session_init_infos.append(init_info)

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
                    utc_time = datetime.datetime.fromtimestamp(unix_timestamp)

                    for key, val in raw.items():
                        row = {'temp': val, 'device': key}
                        # row['datetime'] = utc_time.isoformat()
                        row['datetime'] = utc_time
                        row['unix_timestamp'] = unix_timestamp
                        row['uptime'] = uptime
                        row['session_x'] = session_x
                        rows.append(row)

        session_df = pd.DataFrame(rows)
        session_dfs.append(session_df)

    all_df = pd.concat(session_dfs, ignore_index=True)
    return all_df


def label_xaxis_dates(ax):
    for tick in ax.get_xticklabels():
        tick.set_rotation(30.)

    def date_format(tick_value, tick_pos):
        return datetime.datetime.fromtimestamp(tick_value).isoformat()

    ax.xaxis.set_major_formatter(date_format)


def main():
    import kwplot
    plt = kwplot.autoplt()
    sns = kwplot.autosns()

    alias = {
        '3090': 'nvctrl GeForce GTX 1080 Ti 1 temp',
        '1080ti': 'nvctrl GeForce RTX 3090 0 temp',
        # 'cpu': 'lmsensor coretemp-isa-0000 Package id 0',
    }

    all_df = read_psensor_log()
    unique_rawdevs = all_df.device.unique()
    for rawdev in unique_rawdevs:
        cpu_prefix = 'lmsensor coretemp-isa'
        if rawdev.startswith(cpu_prefix):
            suffix = rawdev[len(cpu_prefix):].split(' ', 1)[1].strip()
            alias['CPU ' + suffix] = rawdev
        if 'nvctrl' in rawdev and 'temp' in rawdev:
            alias['GPU ' + rawdev[7:-5]] = rawdev

    mapper = ub.invert_dict(alias)

    all_df['device'] = all_df['device'].apply(lambda x: mapper.get(x, None))
    all_df = all_df[all_df['device'].apply(lambda x: x is not None)]

    delta = datetime.timedelta(hours=72)
    min_time = datetime.datetime.now() - delta
    is_recent = all_df.datetime > min_time
    recent_df = all_df[is_recent]

    chosen = recent_df
    # chosen = all_df

    if 0:

        pivtbl = recent_df.pivot('unix_timestamp', 'device', 'temp')
        pivtbl = pivtbl.sort_index()
        smoothed_rows = []
        for window_idxs in ub.iter_window(list(range(len(pivtbl))), size=10):
            window = pivtbl.iloc[list(window_idxs)]
            max_val = window.max(axis=0, skipna=True)
            for k, v in max_val.to_dict().items():
                smoothed_rows.append({
                    'unix_timestamp': window.index[1],
                    'device': k,
                    'temp': v,
                })

        max_extra = pd.DataFrame(smoothed_rows)
        sns.lineplot(data=max_extra, x='unix_timestamp', y='temp', hue='device')

        df = recent_df.copy()
        df['device'] = df['device'].apply(lambda x: 'Core' if x.startswith('Core') else x)
        df['time'] = df['unix_timestamp'].apply(datetime.datetime.fromtimestamp)

    plt.gcf().clf()
    # sns.lineplot(data=chosen, x='unix_timestamp', y='temp', hue='device')

    for xx, (sess, group) in enumerate(chosen.groupby('session_x')):
        # ax.cla()
        ax = plt.gca()
        sns.lineplot(data=group, x='unix_timestamp', y='temp', hue='device', legend=xx == 0)

    label_xaxis_dates(ax)
    ax.figure.subplots_adjust(bottom=0.2)
    ax.set_ylim(0, 100)
    plt.locator_params(axis='y', nbins=10)

    # ci_df = pd.concat([max_extra, recent_df])
    # ci_df['device'] = ci_df['device'].apply(lambda x: 'Core' if x.startswith('Core') else x)
    # sns.lineplot(data=ci_df, x='unix_timestamp', y='temp', hue='device')

    # from matplotlib.dates import date2num
    # all_df['date_ord'] = all_df['datetime'].map(lambda a: date2num(a))

    # sns.lineplot(data=pt)
    # sns.lineplot(data=recent_df, x='unix_timestamp', y='temp', hue='device')
    # sns.regplot(data=recent_df, x='unix_timestamp', y='temp', hue='device')