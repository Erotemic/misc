import os
import re
from os.path import join, basename, exists
import ubelt as ub

root_fpath = '/media/joncrall/raid/'
blocklist = {'docker', 'data', 'netharn-work', 'code', 'cache',
             'SteamLibrary', 'venv3', 'venv', 'venv2', 'remote', 'Qt'}


block_patterns = [
    # Don't start with a dot
    re.compile(r'\..*')
]

# Block processing of any directory that contains a file with this name
blocked_fnames = {
    '.git',
}


class Inventory:
    """

    Ignore:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc'))
        >>> from inventory import *  # NOQA
        >>> from inventory import _demodata_files
        >>> dpath = ub.ensure_app_cache_dir('pfile/inv')
        >>> fpaths = _demodata_files(dpath=dpath)
        >>> self = Inventory(dpath)
        >>> self.build()
        >>> #self.build_hashes()
        >>> self.likely_duplicates()
    """
    def __init__(self, root_fpath, blocklist=set()):
        self.root_fpath = root_fpath
        self.blocklist = blocklist
        # self.all_fpaths = None
        # self.all_hashes = None
        self.pfiles = None

    def build(self):
        all_fpaths = []
        blocklist = self.blocklist
        for root, dnames, fnames in os.walk(self.root_fpath):
            if len(blocked_fnames &  set(fnames)) > 0:
                dnames.clear()
                continue

            print('walking = {!r}'.format(root))
            blocked_dnames = blocklist & set(dnames)
            for pat in block_patterns:
                blocked_dnames.update({
                    dname for dname in dnames if pat.match(dname)})
            for dname in blocked_dnames:
                dnames.remove(dname)

            for f in fnames:
                fpath = join(root, f)
                all_fpaths.append(fpath)

        self.pfiles = [ProgressiveFile(f) for f in all_fpaths]
        # self.all_fpaths = all_fpaths

    def build_hashes(self, max_workers=6):
        """
        max_workers = 6
        """
        pfiles = self.pfiles
        ProgressiveFile.parallel_refine(pfiles, step=2, mode='thread',
                                        max_workers=max_workers, verbose=1)
        # from kwcoco.util.util_futures import JobPool  # NOQA
        # # jobs = JobPool(mode='thread', max_workers=2)
        # jobs = JobPool(mode='process', max_workers=max_workers)

        # for fpath in ub.ProgIter(self.all_fpaths, desc='submit hash jobs'):
        #     # jobs.submit(ub.hash_file, fpath, hasher='xx64', maxbytes=1e3)
        #     jobs.submit(ub.hash_file, fpath, hasher='xx64', maxbytes=1e3)

        # self.all_hashes = [
        #     job.result()
        #     for job in ub.ProgIter(
        #         jobs.jobs, desc='collect hash jobs', adjust=0, freq=1)
        # ]

    def likely_duplicates(self, thresh=0.5):
        pfiles = self.pfiles
        # thresh = 0.5

        def _likely_duplicates(pfiles):
            new_groups = {}
            groups = ProgressiveFile.group_pfiles(pfiles)
            for key, group in groups.items():
                if len(group) > 1 and key[-1] < thresh:
                    for pfile in group:
                        pfile.refine()
                    regrouped  = _likely_duplicates(pfiles)
                    new_groups.update(regrouped)
                else:
                    new_groups[key] = group
            return new_groups

        groups = _likely_duplicates(pfiles)

        final = {k: v for k, v in groups.items() if len(v) > 1}
        return final


def progressive_refine_worker(hasher, fpath, parts, pos, curr_blocksize,
                              step_idx, size):
    if len(parts) and parts[-1] == 1:
        return None

    num_steps = max(step_idx - len(parts) + 1, 0)

    if num_steps == 0:
        return None

    next_parts = []

    if len(parts) == 0:
        # FIrst part is just the size
        size = os.stat(fpath).st_size
        frac = 1 if pos == size else 0
        part = ('', pos, size, frac)
        num_steps -= 1
        next_parts.append(part)

    if num_steps > 0:
        with open(fpath, 'rb') as file:
            if pos:
                file.seek(pos)

            for _ in range(num_steps):
                buf = file.read(curr_blocksize)
                readsize = len(buf)
                pos += readsize
                if readsize > 0:
                    hasher.update(buf)
                    hash_chunk = hasher.hexdigest()
                    frac = round(pos / size, 4)
                    part = (hash_chunk, pos, size, frac)
                    next_parts.append(part)
                    # Double the amount of data read if the previous wasnt
                    # enough
                    curr_blocksize *= 2
                else:
                    break
    return hasher, next_parts, pos, curr_blocksize, size


class ProgressiveFile(ub.NiceRepr):
    """
    Doctest:
        >>> # Create a directory filled with random files
        >>> fpaths = _demodata_files()
        >>> pfile = ProgressiveFile(fpaths[0])
        >>> pfile.size
        >>> pfile.refine()
    """

    # TODO:
    #     Some object that can take multiple pfiles and refine their
    #     identifiers to a target specification in parallel

    def __init__(pfile, fpath):
        from ubelt.util_hash import _rectify_hasher
        pfile.fpath = fpath
        pfile._hash = None
        pfile._size = None
        # pfile._hgen = pfile.hash_generator()

        pfile._parts = []
        pfile._hasher = _rectify_hasher('xx64')()
        pfile._curr_blocksize = 65536
        pfile._pos = 0

    def __nice__(pfile):
        MODE = 1
        if MODE == 0:
            return pfile.fpath
        else:
            s = ub.shrinkuser(pfile.fpath)
            if len(pfile._parts) == 0:
                s += ', ?'
            else:
                f = pfile._parts[-1]
                s += ', {}'.format(f)
            return s

    @property
    def curr_step(pfile):
        # Return the number of times this has been refined
        return len(pfile._parts) - 1

    @property
    def can_refine(pfile):
        """
        Return if its possible to refine the identity even further
        """
        return len(pfile._parts) == 0 or pfile._parts[-1][-1] < 1

    @property
    def size(pfile):
        if pfile._size is None:
            pfile._size = os.stat(pfile.fpath).st_size
        return pfile._size

    def step_id(pfile, step_idx):
        if step_idx < 0:
            # We know nothing at this point
            return ('', -1, -1, -1)
        if step_idx >= len(pfile._parts):
            # If we are past the step_idx, return the last one if we cant refine
            if pfile.can_refine:
                raise ValueError('step_idx not computed')
            else:
                return pfile._parts[-1]
        else:
            return pfile._parts[step_idx]

    def refine(pfile):
        """
        Refines the calculation of the identity by one step
        """
        step_idx = pfile.curr_step + 1
        pfile.refined_to(step_idx)
        return pfile.curr_step == step_idx

    def refined_to(pfile, step_idx):
        """
        Ensures we have refined by at least N steps.
        """
        pfiles = [pfile]
        mode = 'serial'
        verbose = 0
        max_workers = 0
        # reuse code to run in serial
        ProgressiveFile.parallel_refine(pfiles, mode=mode, step_idx=step_idx,
                                        max_workers=max_workers,
                                        verbose=verbose)
        return pfile.step_id(step_idx)

    def maybe_equal(pfile, pfile2, thresh=0.2):
        """
        Test to see if at least the first ``thresh`` fractions of the files are
        the same. A False result is always correct. A True result has some
        probability of being incorrect.
        """
        import itertools as it
        for idx in it.count():
            # Ensure the files can be compared at this level
            part1 = pfile.refined_to(idx)
            part2 = pfile2.refined_to(idx)
            if part1 != part2:
                assert part1[0:3] != part2[0:3]
                # Files are 100% not the same
                return False
            frac1 = part1[3]
            if frac1 >= thresh:
                # At least the first fractions of the file are the same
                return True

    def __eq__(pfile, pfile2):
        pass

    @classmethod
    def group_pfiles(cls, pfiles):
        """
        Creates groups of pfiles that *might* be the same.

        Example:
            >>> fpaths = _demodata_files()
            >>> pfiles = [ProgressiveFile(f) for f in fpaths]
            >>> groups1 = ProgressiveFile.group_pfiles(pfiles)
            >>> for pfile in pfiles:
            >>>     pfile.refine()
            >>> groups2 = ProgressiveFile.group_pfiles(pfiles)
        """
        size_groups = ub.group_items(pfiles, key=lambda x: x.size)
        final_groups = {}

        for group in size_groups.values():
            # we have to use the minimum refine step available
            # for any unfinished pfile to ensure consistency
            unfinished = [pfile for pfile in group if pfile.can_refine]
            if len(unfinished) == 0:
                step_idx = float('inf')
            else:
                step_idx = min(pfile.curr_step for pfile in unfinished)

            for pfile in group:
                pfile.step_id(step_idx)

            step_groups = ub.group_items(group, key=lambda x: x.step_id(step_idx))
            final_groups.update(step_groups)
        return final_groups

    @classmethod
    def parallel_refine(cls, pfiles, step_idx, mode='serial', max_workers=6, verbose=0):
        """
            Ignore:
                fpaths = _demodata_files(
                        num_files=500, size_pool=[10, 20, 30], pool_size=2)
            >>> # Create a directory filled with random files
            >>> fpaths = _demodata_files()
            >>> pfiles = [ProgressiveFile(f) for f in fpaths]
            >>> with ub.Timer('step'):
            >>>     step_idx = 2
            >>>     ProgressiveFile.parallel_refine(pfiles, step_idx)
        """
        from kwcoco.util.util_futures import JobPool  # NOQA
        # jobs = JobPool(mode='thread', max_workers=2)

        # TODO: Can we make xxhash pickleable
        # https://github.com/ifduyue/python-xxhash/issues/24
        jobs = JobPool(mode=mode, max_workers=max_workers)

        for pfile in ub.ProgIter(pfiles, desc='submit hash jobs', verbose=verbose):

            hasher = pfile._hasher
            parts = pfile._parts
            fpath = pfile.fpath
            pos = pfile._pos
            size = pfile._size
            curr_blocksize = pfile._curr_blocksize

            job = jobs.submit(
                progressive_refine_worker, hasher, fpath, parts, pos,
                curr_blocksize, step_idx, size)
            job.pfile = pfile

        for job in ub.ProgIter(jobs.as_completed(), total=len(jobs),
                               desc='collect hash jobs', verbose=verbose):
            pfile = job.pfile
            result = job.result()
            if result is not None:
                hasher, next_parts, pos, curr_blocksize, size = result
                pfile._hasher = hasher
                pfile._parts.extend(next_parts)
                pfile._pos = pos
                pfile._size = size
                pfile._curr_blocksize = curr_blocksize

    # Old serial code (maybe worth another look?)
    # def hash_generator(pfile):
    #     """
    #     The idea is that we will hash the first few bytes of a file
    #     This will allow us to group files that *might* overlap. In the case
    #     where there are conflicts, we can continue hashing until we have
    #     hashed all data, or we have hashed enough to be confident.
    #     """
    #     from ubelt.util_hash import _rectify_hasher
    #     # pfile._hash =
    #     # ub.hash_file(pfile.fpath, hasher='xx64')
    #     start_blocksize = 65536
    #     hasher = _rectify_hasher('xx64')()
    #     pfile._parts = []
    #     pos = 0
    #     size = pfile.size
    #     frac = 1 if pos == size else 0
    #     part = ('', pos, size, frac)
    #     pfile._parts.append(part)
    #     yield part
    #     curr_blocksize = start_blocksize
    #     while pos < size:
    #         with open(pfile.fpath, 'rb') as file:
    #             if pos:
    #                 file.seek(pos)
    #             buf = file.read(curr_blocksize)
    #         readsize = len(buf)
    #         pos += readsize
    #         if readsize > 0:
    #             hasher.update(buf)
    #             hash_chunk = hasher.hexdigest()
    #             frac = round(pos / size, 4)
    #             part = (hash_chunk, pos, size, frac)
    #             pfile._parts.append(part)
    #             yield part
    #             # Double the amount of data read if the previous wasnt
    #             # enough
    #             curr_blocksize *= 2
    #         else:
    #             break


####

def main():
    if 0:
        # TODO: progressive hashing data structure

        inv1 = Inventory('/media/joncrall/raid/', blocklist)
        inv2 = Inventory('/media/joncrall/media', blocklist)

        self = inv1  # NOQA

        inv1.build()
        inv2.build()

    if 0:
        fpath = inv1.all_fpaths[0]
        pfile = ProgressiveFile(fpath)

        fpath1 = '/media/joncrall/raid/unsorted/yet-another-backup/card-usb-drive/Transfer/Zebras/DownloadedLibraries/lightspeed/solve_triu.m'
        fpath2 = '/media/joncrall/raid/unsorted/yet-another-backup/card-usb-drive/Zebras/downloaded_libraries/lightspeed/solve_triu.m'

        fpath1 = '/media/joncrall/raid/Applications/Wii/WiiHacksAndStuff/CurrentHacks/Falco/DarkFalco02.pcs'
        fpath2 = '/media/joncrall/raid/Applications/Wii/WiiHacksAndStuff/CurrentHacks/Ivysaur/Kraid-v2-Ivy.pcs'

        pfile = pfile1 = ProgressiveFile(fpath1)
        pfile2 = ProgressiveFile(fpath2)

        pfile.maybe_equal(pfile2, thresh=0.1)

        fpath_demodata = inv1.all_fpaths[::len(inv1.all_fpaths) // 500]
        # fpaths = hash_groups1_dup['ef46db3751d8e999']
        pfiles_demodata = [ProgressiveFile(f) for f in fpath_demodata]


        def progressive_duplicates(pfiles, idx=1):
            step_ids = [pfile.refined_to(idx) for pfile in ub.ProgIter(pfiles)]
            final_groups = {}
            grouped = ub.group_items(pfiles, step_ids)
            for key, group in grouped.items():
                if len(group) > 1:
                    if all(not g.can_refine for g in group):
                        # Group is ~100% a real duplicate
                        final_groups[key] = group
                    else:
                        pfiles = group
                        deduped = progressive_duplicates(pfiles, idx=idx + 1)
                        final_groups.update(deduped)
                else:
                    final_groups[key] = group
            return final_groups

        pfiles = pfiles_demodata
        final_groups = progressive_duplicates(pfiles)

        for key, group in final_groups.items():
            if len(group) > 1:
                print('key = {!r}'.format(key))
                print('group = {}'.format(ub.repr2(group, nl=1)))

        inv1.build_hashes()
        inv2.build_hashes()

        hash_groups1 = ub.group_items(inv1.all_fpaths, inv1.all_hashes)
        hash_groups2 = ub.group_items(inv2.all_fpaths, inv2.all_hashes)

        hash_groups1_dup = {k: v for k, v in hash_groups1.items() if len(v) > 1}
        hash_groups2_dup = {k: v for k, v in hash_groups2.items() if len(v) > 1}
        len(hash_groups1_dup)
        len(hash_groups2_dup)

        # common = set(hash_groups1) & set(hash_groups2)
        # xdev.set_overlaps(hash_groups1, hash_groups2)

        fnames1 = ub.group_items(inv1.all_fpaths, key=basename)
        fnames2 = ub.group_items(inv2.all_fpaths, key=basename)

        missing = ub.dict_diff(fnames2, fnames1)
        sorted(ub.flatten(missing.values()))
        len(missing)

        fpath_demodata = inv1.all_fpaths[::len(inv1.all_fpaths) // 500]

        def internal_deduplicate(self):
            hash_groups = ub.group_items(self.all_fpaths, self.all_hashes)
            hash_groups_dup = {k: v for k, v in hash_groups.items() if len(v) > 1}

            from os.path import dirname

            hash_groups_dup['ef46db3751d8e999']

            for key, values in hash_groups_dup.items():
                for v in values:
                    if v.endswith('.avi'):
                        break

                [basename(v) for v in values]
                [dirname(v) for v in values]


def _demodata_files(dpath=None, num_files=10, pool_size=3, size_pool=None):
    import random
    import string

    def _random_data(rng, num):
        return ''.join([rng.choice(string.hexdigits) for _ in range(num)])

    def _write_random_file(dpath, part_pool, size_pool, rng):
        namesize = 16
        # Choose 1, 4, or 16 parts of data
        num_parts = rng.choice(size_pool)
        chunks = [rng.choice(part_pool) for _ in range(num_parts)]
        contents = ''.join(chunks)
        fname_noext = _random_data(rng, namesize)
        ext = ub.hash_data(contents)[0:4]
        fname = '{}.{}'.format(fname_noext, ext)
        fpath = join(dpath, fname)
        with open(fpath, 'w') as file:
            file.write(contents)
        return fpath

    if size_pool is None:
        size_pool = [1, 4, 16]

    if dpath is None:
        dpath = ub.ensure_app_cache_dir('pfile/random')
    rng = random.Random(0)
    # Create a pool of random chunks of data
    chunksize = 65536
    part_pool = [_random_data(rng, chunksize) for _ in range(pool_size)]
    # Write 100 random files that have a reasonable collision probability
    fpaths = [_write_random_file(dpath, part_pool, size_pool, rng)
              for _ in ub.ProgIter(range(num_files), desc='write files')]

    for fpath in fpaths:
        assert exists(fpath)
    return fpaths


def benchmark():
    """
    apt-get install xxhash
    """
    import timerit
    import ubelt as ub
    from kwcoco.util.util_futures import JobPool  # NOQA
    ti = timerit.Timerit(1, bestof=1, verbose=3)

    max_workers = 6

    fpath_demodata = _demodata_files()
    for timer in ti.reset('hash_file(hasher=xx32)'):
        with timer:
            for fpath in fpath_demodata:
                ub.hash_file(fpath, hasher='xx32')

    for timer in ti.reset('hash_file(hasher=xx64)'):
        with timer:
            for fpath in fpath_demodata:
                ub.hash_file(fpath, hasher='xx64')

    for timer in ti.reset('hash_file(hasher=xxhash) - serial'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='serial', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xxhash')
            results = [job.result() for job in jobs.jobs]

    for timer in ti.reset('hash_file(hasher=xxhash) - thread'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='thread', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xx64')
            results = [job.result() for job in jobs.jobs]

    for timer in ti.reset('hash_file(hasher=xxhash) - process'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='process', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xx64')
            results = [job.result() for job in jobs.jobs]

    for timer in ti.reset('cmd-xxh32sum'):
        with timer:
            for fpath in fpath_demodata:
                ub.cmd(['xxh32sum', fpath])['out'].split(' ')[0]

    for timer in ti.reset('cmd-xxh64sum'):
        with timer:
            for fpath in fpath_demodata:
                ub.cmd(['xxh64sum', fpath])['out'].split(' ')[0]

    for timer in ti.reset('cmd-xxh64sum-detatch'):
        with timer:
            jobs = [
                ub.cmd(['xxh64sum', fpath], detatch=True)
                for fpath in fpath_demodata
            ]
            results = [
                job['proc'].communicate()[0].split(' ')[0]
                for job in jobs
            ]

    for timer in ti.reset('cmd-sha1sum'):
        with timer:
            for fpath in fpath_demodata:
                ub.cmd(['sha1sum', fpath])['out'].split(' ')[0]

    for timer in ti.reset('hash_file(hasher=sha1)'):
        with timer:
            for fpath in fpath_demodata:
                ub.hash_file(fpath, hasher='sha1')

# query = 'IMG_20150821_180955373'
# for fpath in all_fpaths:
#     if basename(fpath).startswith(query):
#         print('fpath = {!r}'.format(fpath))

# import ubelt as ub
# fpath_to_info = {}
# for fpath in ub.ProgIter(all_fpaths):
#     info = {
#         'fname': basename(fpath),
#         'hash': ub.hash_file(fpath)
#     }
#     fpath_to_info[fpath] = info
