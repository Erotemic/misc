import stat
import ubelt as ub
import pathlib
import requests
import os


def main_requests():
    urls = [
        'https://google.com',
        'https://whitehouse.gov',
        'https://cmake.org',
        'https://stackoverflow.com/',
        'https://reddit.com',
        'https://github.com/ipfs/go-ipfs',
    ]
    times = {}
    for url in urls:
        with ub.Timer() as timer:
            resp = requests.get(url)
            print(resp.text)
        times[url] = timer.elapsed
    print('times = {}'.format(ub.repr2(times, nl=1)))
    total = sum(times.values())
    print('total = {!r}'.format(total))


def ensure_selenium_chromedriver():
    """
    os.environ['webdriver.chrome.driver'] = ensure_selenium_chromedriver()
    """
    import zipfile
    timeout = 5.0

    def latest_version():
        rsp = requests.get('http://chromedriver.storage.googleapis.com/LATEST_RELEASE', timeout=timeout)
        if rsp.status_code != 200:
            raise Exception
        version = rsp.text.strip()
        return version

    # version = latest_version()
    # version = '91.0.4472.19'
    # version = '90.0.4430.24'
    # version = '92.0.4515.107'
    version = '96.0.4664.45'

    known_hashs = {
        '91.0.4472.19': '49622b740b1c7e66b87179a2642f6c57f21a97fc844c84b30a48',
        '90.0.4430.24': 'b85313de6abc1b44f26a0e12e20cb66657b840417f5ac6018946',
        '92.0.4515.107': '844c0e04bbbfd286617af2d7facd3d6cf7d3491b1e78120f8e0',
        '96.0.4664.45': 'ba0f0979e1b43930c5890ce24e904553d41985d83c2118bd000c31451efc6f5c5e5cf9c52a1637fbb554c1577a929cd8446eff3162f443b4cc159e6b972d3099',
    }
    url = 'http://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip'.format(version)
    bin_dpath = pathlib.Path(ub.expandpath('~/.local/bin'))
    download_dpath = bin_dpath / f'chromedriver_{version}'
    download_dpath.mkdir(exist_ok=True, parents=True)

    zip_fpath = ub.grabdata(
        url, hash_prefix=known_hashs.get(version, 'unknown-version'),
        dpath=download_dpath,
    )
    zip_fpath = pathlib.Path(zip_fpath)
    # dpath = zip_fpath.parent

    # TODO: version the binary
    chromedriver_fpath_real = download_dpath / 'chromedriver'
    chromedriver_fpath_link = bin_dpath / 'chromedriver'

    if True or (not chromedriver_fpath_real.exists() or not chromedriver_fpath_link.exists()):
        # Also check hash?

        zfile = zipfile.ZipFile(str(zip_fpath))
        try:
            fpath = zfile.extract(
                'chromedriver', path=chromedriver_fpath_real.parent)
        finally:
            zfile.close()

        chromedriver_fpath_real_ = pathlib.Path(fpath)
        assert chromedriver_fpath_real_.exists()
        ub.symlink(chromedriver_fpath_real_, chromedriver_fpath_link,
                   overwrite=True)

        if not ub.WIN32:
            print('add permission chromedriver_fpath_real_ = {!r}'.format(chromedriver_fpath_real_))
            st = os.stat(chromedriver_fpath_real_)
            os.chmod(chromedriver_fpath_real_, st.st_mode | stat.S_IEXEC)

        os.environ['PATH'] = os.pathsep.join(
            ub.oset(os.environ['PATH'].split(os.pathsep)) |
            ub.oset([str(chromedriver_fpath_link.parent)]))
    return chromedriver_fpath_link


def main_selenium():
    from selenium import webdriver
    ensure_selenium_chromedriver()
    # url = 'https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags/'
    # url = 'https://www.reddit.com/r/TheSilphArena/comments/jr2ee9/season_5_little_cup_meta_moves_infographic/'
    # url = 'https://en.wikipedia.org/wiki/Prime_number'
    # url = 'https://networkx.org/documentation/networkx-1.10/reference/generated/networkx.algorithms.simple_paths.all_simple_paths.html'
    url = 'https://pypi.org/project/networkx/'
    with ub.Timer() as timer:
        driver = webdriver.Chrome()
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(30)
    print('timer.elapsed = {!r}'.format(timer.elapsed))


if __name__ == '__main__':
    """
    https://discuss.ipfs.io/t/ipfs-daemon-slows-regular-browsing-to-a-crawl/13064/6

    CommandLine:
        python ~/misc/test_https_speed.py
    """
    # main_requests()
    main_selenium()
