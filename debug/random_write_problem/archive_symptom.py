#!/usr/bin/env python3
import scriptconfig as scfg
import ubelt as ub


class ArchiveSymptomConfig(scfg.DataConfig):
    input_fpaths = scfg.Value(
        [], nargs='+', position=1, help='path to the files to archive', type=str)


def main(cmdline=1, **kwargs):
    """
    Example:
        >>> # xdoctest: +SKIP
        >>> cmdline = 0
        >>> kwargs = dict(srcs=['i gq'])
        >>> main(cmdline=cmdline, **kwargs)
    """
    config = ArchiveSymptomConfig.legacy(cmdline=cmdline, data=kwargs)
    print('config = ' + ub.urepr(dict(config), nl=1))

    home = ub.Path.home()
    archive_dpath = home / 'misc/debug/random_write_problem/symptoms'
    archive_dpath.ensuredir()

    move_tasks = []

    assert archive_dpath.exists()
    assert archive_dpath.is_dir()

    for input_fpath in ub.ProgIter(config.input_fpaths, desc='building move tasks'):
        input_fpath = ub.Path(input_fpath)
        assert input_fpath.exists()
        input_fpath.is_file()

        abs_fpath = input_fpath.absolute()

        rel_fpath = abs_fpath.relative_to(home)
        dst_fpath = archive_dpath / rel_fpath

        assert not dst_fpath.exists()
        move_tasks.append({'src': abs_fpath, 'dst': dst_fpath})

    print('move_tasks = {}'.format(ub.urepr(move_tasks, nl=1)))
    import rich.prompt
    ans = rich.prompt.Confirm.ask('Do these moves look right?')
    if ans:
        for task in ub.ProgIter(move_tasks):
            src = task['src']
            dst = task['dst']
            assert dst.is_relative_to(archive_dpath)
            dst.parent.ensuredir()
            assert not dst.exists()
            src.move(dst)

if __name__ == '__main__':
    """

    CommandLine:
        python ~/misc/debug/random_write_problem/archive_symptom.py
        python -m archive_symptom

    """
    main()
