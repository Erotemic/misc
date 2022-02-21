import os
from os.path import join


def walk_with_scandir(root_dpath):
    stack = [root_dpath]
    while stack:
        dpath = stack.pop()
        try:
            scan_iter = os.scandir(dpath)
        except PermissionError:
            continue
        else:
            for entry in scan_iter:
                yield entry.path
                if entry.is_dir():
                    stack.append(entry.path)


def walk_with_walk(root_dpath):
    for r, fs, ds in os.walk(root_dpath):
        for f in fs:
            yield join(r, f)
        for d in ds:
            yield join(r, d)


def main():
    import ubelt as ub
    root_dpath = ub.Path('/etc')

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=2)
    for timer in ti.reset('time'):
        with timer:
            items1 = sorted(walk_with_scandir(root_dpath))

    for timer in ti.reset('time'):
        with timer:
            items2 = sorted(walk_with_walk(root_dpath))

    len(items1)
    len(items2)
