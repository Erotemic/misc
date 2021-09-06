def notes_on_md5():
    """

    Not only is MD5 a weak hash algorithm, its also a broken one.

    The academic work outlined here: [1] describes more details.

    https://cryptography.hyperlink.cz/2006/diplomka.pdf


    Python implementation of md5 itself: https://github.com/timvandermeij/md5.py

    http://www.win.tue.nl/hashclash/fastcoll_v1.0.0.5_source.zip

    sudo apt-get install autoconf automake libtool libperl-dev
    sudo apt-get install zlib1g-dev libbz2-dev
    sudo apt-get install libtool
    git clone https://github.com/cr-marcstevens/hashclash

    ./install_boost.sh
    autoreconf --install
    ./configure --with-boost=$(pwd)/boost-1.57.0 --without-cuda

    References:
        [1] : https://cryptography.hyperlink.cz/MD5_collisions.html
    """
    from kwcoco.data.grab_spacenet import Archive
    workdir = ub.ensure_app_cache_dir('pwdemo/md5_collision')
    import os
    os.chdir(workdir)

    zip_fpath = ub.grabdata(
        'http://www.win.tue.nl/hashclash/fastcoll_v1.0.0.5_source.zip',
        dpath=workdir, hash_prefix='8a3ad700945cb803c7ecfddca20cae3f147f171813b5b03f85b8')
    boost_zip = ub.grabdata(
        'https://boostorg.jfrog.io/artifactory/main/release/1.76.0/source/boost_1_76_0.tar.gz',
        hash_prefix='7bd7ddceec1a1dfdcbdb3e609b60d01739c38390a5f956385a12f3122049f0ca',
        hasher='sha256', dpath=workdir)

    extracted_fpaths = Archive(zip_fpath).extractall(workdir)
    boost_paths = Archive(boost_zip).extractall(workdir)

    bcmd = f'bash {workdir}/boost_1_76_0/bootstrap.sh --prefix={workdir}/boost_build --without-libraries=python,graph,graph_parallel,wave'
    ub.ensuredir(f'{workdir}/boost_build')
    ub.cmd(bcmd, verbose=3, cwd=f'{workdir}/boost_1_76_0')
    ub.cmd('./b2', verbose=3, cwd=f'{workdir}/boost_1_76_0', shell=True)

    command = ub.paragraph(
        f'''
        gcc
        {' '.join(extracted_fpaths)}
        -I {workdir}/boost_1_76_0
        -L {workdir}/boost_1_76_0/stage/lib
        -l libboost_system
        ''')
    _ = ub.cmd(command, verbose=3, cwd=f'{workdir}')
