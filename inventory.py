"""

"""
import os
import re
from os.path import join, basename, exists, dirname
import ubelt as ub
import itertools as it

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

    def build_hashes(self, step_idx=1, mode='thread', max_workers=0,
                     verbose=1):
        """
        Note: threading is faster for large number of files. Unfortunately we
        cant use process mode because we cant pickle hashers.

        max_workers = 6
        """
        pfiles = self.pfiles
        ProgressiveFile.parallel_refine(pfiles, step_idx=step_idx, mode=mode,
                                        max_workers=max_workers,
                                        verbose=verbose)

    def likely_duplicates(self, thresh=0.5, verbose=1):
        return ProgressiveFile.likely_duplicates(self.pfiles, thresh=thresh, verbose=verbose)


class ProgressiveFile(ub.NiceRepr):
    """
    Holds onto a file and stores a progressively more precise hash-id.

    This can be used for probabalistically determining if files are the same
    with much less computation.

    Doctest:
        >>> # Create a directory filled with random files
        >>> fpaths = _demodata_files()
        >>> pfile = ProgressiveFile(fpaths[0])
        >>> pfile.size
        >>> pfile.refine()
    """

    def __init__(pfile, fpath):
        from ubelt.util_hash import _rectify_hasher
        pfile.fpath = fpath
        pfile._hash = None
        pfile._size = None
        # pfile._hgen = pfile.hash_generator()

        pfile._parts = []
        pfile._hasher = _rectify_hasher('xx64')()
        pfile._curr_blocks = 1
        pfile._pos = 0

    def __nice__(pfile):
        MODE = 1
        if MODE == 0:
            return pfile.fpath
        else:
            s = repr(pfile.fpath)
            if len(pfile._parts) == 0:
                s += ', ?'
            else:
                f = pfile._parts[-1]
                s += ', {}'.format(f)
            return s

    def _check_integrity(pfile):
        for part in pfile._parts[1:]:
            # Ensure that each partial hash corresponds with the actual partial
            # hash.
            target = ub.hash_file(
                pfile.fpath, blocksize=int(2 ** 20), maxbytes=part[1],
                hasher='xx64')
            if target != part[0]:
                raise AssertionError('The hashes do not match!')

    @property
    def curr_step_idx(pfile):
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
            pfile.refined_to(step_idx=0)
            # pfile._size = os.stat(pfile.fpath).st_size
        return pfile._size

    def step_id(pfile, step_idx=None):
        if step_idx is None:
            step_idx = pfile.curr_step_idx

        if step_idx < 0:
            # We know nothing at this point
            return ('', -1, -1, -1)
        if step_idx >= len(pfile._parts):
            # If we are past the step_idx AND we can't refine, then we can
            # safely return the last one.
            if not pfile.can_refine:
                return pfile._parts[-1]
            else:
                raise ValueError('step_idx not computed')
        else:
            return pfile._parts[step_idx]

    def refine(pfile):
        """
        Refines the calculation of the identity by one step
        """
        step_idx = pfile.curr_step_idx + 1
        pfile.refined_to(step_idx)
        return pfile.curr_step_idx == step_idx

    def refined_to(pfile, step_idx):
        """
        Ensures we have refined by at least N steps.

        Ignore:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc'))
            >>> from inventory import *  # NOQA
            >>> from inventory import _demodata_files
            >>> fpaths = _demodata_files(num_files=1, size_pool=[1000], pool_size=2)

            >>> pfile = ProgressiveFile(fpaths[0])
            >>> step_idxs = [-1, 0, 3]
            >>> print(chr(10) + '----')
            >>> for step_idx in step_idxs:
            >>>     print('step_idx = {!r}'.format(step_idx))
            >>>     step_id = pfile.refined_to(step_idx)
            >>>     print('step_id = {!r}'.format(step_id))
            >>>     print('pfile = {}'.format(pfile))

            >>> pfile = ProgressiveFile(fpaths[0])
            >>> step_idxs = [1, 5, 3, 0, -1, 100]
            >>> print(chr(10) + '----')
            >>> for step_idx in step_idxs:
            >>>     print('step_idx = {!r}'.format(step_idx))
            >>>     step_id = pfile.refined_to(step_idx)
            >>>     print('step_id = {!r}'.format(step_id))
            >>>     print('pfile = {}'.format(pfile))

            >>> pfile = ProgressiveFile(fpaths[0])
            >>> step_idxs = [1000, -1, 0, 3]
            >>> print(chr(10) + '----')
            >>> for step_idx in step_idxs:
            >>>     print('step_idx = {!r}'.format(step_idx))
            >>>     step_id = pfile.refined_to(step_idx)
            >>>     print('step_id = {!r}'.format(step_id))
            >>>     print('pfile = {}'.format(pfile))
            >>> pfile._check_integrity()
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

    def complete_enough(pfile, byte_thresh=None, frac_thresh=None):
        part = pfile.step_id()
        byte = part[1]
        frac = part[3]
        terms = []
        if frac_thresh is not None:
            terms.append(frac >= frac_thresh)
        if byte_thresh is not None:
            terms.append(byte >= byte_thresh)
        good_enough = any(terms) or len(terms) == 0
        return good_enough

    def maybe_equal(pfile, pfile2, thresh=0.2):
        """
        Test to see if at least the first ``thresh`` fractions of the files are
        the same. A False result is always correct. A True result has some
        probability of being incorrect.
        """
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

    # def __eq__(pfile, pfile2):
    #     pass

    @classmethod
    def likely_duplicates(cls, pfiles, thresh=0.2, verbose=1):
        final_groups = {}
        active_groups = [pfiles]
        mode = 'thread'
        max_workers = 6

        while active_groups:
            group_sizes = list(map(len, active_groups))
            total_active = sum(group_sizes)
            print('Checking {} active groups with {} items'.format(len(active_groups), total_active))
            groups = ub.dict_union(*[
                ProgressiveFile.group_pfiles(g) for g in active_groups
            ])

            # Mark all groups that need refinement
            refine_items = []
            next_groups = []
            for key, group in groups.items():
                if len(group) > 1 and key[-1] < thresh:
                    next_groups.append(group)
                    refine_items.extend([
                        item for item in group if item.step_id()[-1] < thresh
                    ])
                else:
                    # Any group that doesnt need refinment is added to the
                    # solution and will not appear in the next active group
                    final_groups[key] = group

            # Refine any item that needs it
            if len(refine_items):
                # TODO: if there are few enough items, just refine to the
                # threshold?
                ProgressiveFile.parallel_refine(
                    refine_items, mode=mode, step_idx='next',
                    max_workers=max_workers, verbose=verbose)

            # Continue refinement as long as there are active groups
            active_groups = next_groups
        return final_groups

    @classmethod
    def likely_overlaps(cls, pfiles1, pfiles2, thresh=0.2, verbose=1):
        """
        This is similar to finding duplicates, but between two sets of files

        Example:
            >>> fpaths = _demodata_files(num_files=100, rng=0)
            >>> fpaths1 = fpaths[0::2]
            >>> fpaths2 = fpaths[1::2]
            >>> pfiles1 = [ProgressiveFile(f) for f in fpaths1]
            >>> pfiles2 = [ProgressiveFile(f) for f in fpaths2]
            >>> overlap, only1, only2 = ProgressiveFile.likely_overlaps(pfiles1, pfiles2)
            >>> print(len(overlaps))
            >>> print(len(only1))
            >>> print(len(only2))
        """
        final_groups = {}

        # Mark each set of files, so we only refine if a duplicate group
        # contains elements from multiple sets

        set1 = {id(p) for p in pfiles1}
        set2 = {id(p) for p in pfiles2}

        def _membership(p):
            partof = []
            pid = id(p)
            if pid in set1:
                partof.append(1)
            if pid in set2:
                partof.append(2)
            return partof

        pfiles = pfiles1 + pfiles2

        active_groups = [pfiles]
        mode = 'thread'
        max_workers = 6

        if isinstance(thresh, dict):
            frac_thresh = thresh.get('frac', None)
            byte_thresh = thresh.get('byte', None)
        else:
            frac_thresh = thresh
            byte_thresh = thresh

        while active_groups:
            group_sizes = list(map(len, active_groups))
            total_active = sum(group_sizes)
            print('Checking {} active groups with {} items'.format(len(active_groups), total_active))
            groups = ub.dict_union(*[
                ProgressiveFile.group_pfiles(g) for g in active_groups
            ])

            # Mark all groups that need refinement
            refine_items = []
            next_groups = []
            for key, group in groups.items():
                membership = {m for p in group for m in _membership(p)}

                group_frac = key[3]
                group_byte = key[1]
                # Check if we have hashed enough of the file by fraction or
                # number of bytes.
                terms = []
                if frac_thresh is not None:
                    terms.append(group_frac >= frac_thresh)
                if byte_thresh is not None:
                    terms.append(group_byte >= byte_thresh)
                good_enough = any(terms) or len(terms) == 0

                if not good_enough and len(membership) > 1 and len(group) > 1:
                    next_groups.append(group)
                    needs_refine = [
                        item for item in group if not item.complete_enough(
                            frac_thresh=frac_thresh, byte_thresh=byte_thresh)
                    ]
                    refine_items.extend(needs_refine)
                else:
                    # Any group that doesnt need refinment is added to the
                    # solution and will not appear in the next active group
                    final_groups[key] = group

            # Refine any item that needs it
            if len(refine_items):
                # TODO: if there are few enough items, just refine to the
                # threshold?
                ProgressiveFile.parallel_refine(
                    refine_items, mode=mode, step_idx='next',
                    max_workers=max_workers, verbose=verbose)

            # Continue refinement as long as there are active groups
            active_groups = next_groups

        only1 = {}
        only2 = {}
        overlap = {}
        for key, group in final_groups.items():
            membership = {m for p in group for m in _membership(p)}
            if len(membership) == 1:
                if ub.peek(membership) == 1:
                    only1[key] = group
                else:
                    only2[key] = group
            else:
                overlap[key] = group

        return overlap, only1, only2

    @classmethod
    def compatible_step_idx(cls, pfiles):
        """
        Compute the maximum compatible step idx for comparison
        """
        # we have to use the minimum refine step available
        # for any unfinished pfile to ensure consistency
        unfinished = [pfile for pfile in pfiles if pfile.can_refine]
        if len(unfinished) == 0:
            step_idx = float('inf')
        else:
            step_idx = min(pfile.curr_step_idx for pfile in unfinished)
        return step_idx

    @classmethod
    def group_pfiles(cls, pfiles, step_idx=None):
        """
        Creates groups of pfiles that *might* be the same.

        Example:
            >>> fpaths = _demodata_files()
            >>> pfiles = [ProgressiveFile(f) for f in fpaths]
            >>> groups1 = ProgressiveFile.group_pfiles(pfiles)
            >>> for pfile in pfiles:
            >>>     pfile.refine()
            >>> groups2 = ProgressiveFile.group_pfiles(pfiles)
            >>> for pfile in pfiles[0::2]:
            >>>     pfile.refine()
            >>> groups3 = ProgressiveFile.group_pfiles(pfiles)
            >>> for pfile in pfiles[1::2]:
            >>>     pfile.refine()
            >>> groups4 = ProgressiveFile.group_pfiles(pfiles)
        """
        if step_idx is not None:
            # We are given the step idx to use, so do that
            final_groups = ub.group_items(pfiles, key=lambda x: x.step_id(step_idx))
        else:
            # Otherwise do something reasonable
            size_groups = ub.group_items(pfiles, key=lambda x: x.size)
            final_groups = ub.ddict(list)
            for group in size_groups.values():
                # we have to use the minimum refine step available
                # for any unfinished pfile to ensure consistency
                step_idx = ProgressiveFile.compatible_step_idx(group)
                step_groups = ub.group_items(group, key=lambda x: x.step_id(step_idx))
                for key, val in step_groups.items():
                    final_groups[key].extend(val)
        return final_groups

    @classmethod
    def parallel_refine(cls, pfiles, step_idx, mode='serial', max_workers=6,
                        verbose=0):
        """
        Refines the hashids of multiple files

        Ignore:
            >>> # Create a directory filled with random files
            >>> #fpaths = _demodata_files(
            >>> #        num_files=1, size_pool=[30], pool_size=2)
            >>> fpaths = _demodata_files()
            >>> pfiles = [ProgressiveFile(f) for f in fpaths]
            >>> with ub.Timer('step'):
            >>>     step_idx = 2
            >>>     ProgressiveFile.parallel_refine(pfiles, step_idx)
        """
        from kwcoco.util.util_futures import JobPool  # NOQA
        # jobs = JobPool(mode='thread', max_workers=2)

        jobs = JobPool(mode=mode, max_workers=max_workers)

        for pfile in ub.ProgIter(pfiles, desc='submit hash jobs', verbose=verbose):
            # only submit the job if we need to
            parts = pfile._parts
            if pfile.can_refine and (step_idx == 'next' or len(parts) <= step_idx):
                hasher = pfile._hasher
                fpath = pfile.fpath
                pos = pfile._pos
                size = pfile._size
                curr_blocks = pfile._curr_blocks

                job = jobs.submit(
                    progressive_refine_worker, hasher, fpath, parts, pos,
                    curr_blocks, step_idx, size)
                job.pfile = pfile

        for job in ub.ProgIter(jobs.as_completed(), total=len(jobs),
                               desc='collect hash jobs', verbose=verbose):
            pfile = job.pfile
            result = job.result()
            if result is not None:
                hasher, next_parts, pos, curr_blocks, size = result
                pfile._hasher = hasher
                pfile._parts.extend(next_parts)
                pfile._pos = pos
                pfile._size = size
                pfile._curr_blocks = curr_blocks


def progressive_refine_worker(hasher, fpath, parts, pos, curr_blocks,
                              step_idx, size):
    """
    Worker function for progressive file-hash refinement.

    TODO:
        - [ ] Can we make xxhash pickleable?
        https://github.com/ifduyue/python-xxhash/issues/24
    """
    num_parts = len(parts)

    if num_parts and parts[-1] == 1:
        return None

    if step_idx == 'next':
        step_idx = num_parts

    num_steps = max(step_idx - num_parts + 1, 0)

    if num_steps == 0:
        return None

    next_parts = []

    if num_parts == 0:
        # First part is just the size
        size = os.stat(fpath).st_size
        frac = 1 if pos == size else 0
        part = ('', pos, size, frac)
        num_steps -= 1
        next_parts.append(part)

    blocksize = 1048576  # int(2 ** 20)

    if num_steps > 0:
        with open(fpath, 'rb') as file:
            if pos:
                file.seek(pos)

            # DO NOT CHANGE THE BLOCKSIZE (it is much slower that way)
            # Instead just loop over some number of blocks
            while num_steps > 0:
                startpos = pos
                # Read some number of blocks
                for _ in range(curr_blocks):
                    buf = file.read(blocksize)
                    hasher.update(buf)
                    readsize = len(buf)
                    pos += readsize
                    if readsize == 0:
                        break

                if pos > startpos:
                    hash_chunk = hasher.hexdigest()
                    frac = round(pos / size, 6)
                    part = (hash_chunk, pos, size, frac)
                    next_parts.append(part)
                    # Double the number of blocks we read each time
                    curr_blocks *= 2
                else:
                    break
                num_steps -= 1

        if pos == size:
            # We are done hashing, so we can destroy the hasher
            hasher = None

    return hasher, next_parts, pos, curr_blocks, size


####

def main():
    # TODO: progressive hashing data structure
    inv1 = Inventory('/media/joncrall/raid/', blocklist)
    inv2 = Inventory('/media/joncrall/media', blocklist)

    # inv1 = Inventory('/media/joncrall/raid/Applications/NotGames', blocklist)
    # inv2 = Inventory('/media/joncrall/media/Applications/NotGames', blocklist)
    # inv1 = Inventory('/media/joncrall/raid/Applications', blocklist)
    # inv2 = Inventory('/media/joncrall/media/Applications', blocklist)

    self = inv1  # NOQA

    inv1.build()
    inv2.build()

    thresh = {
        'frac': 0.5,
        'byte': 100 * int(2 ** 20)  # only use the first few mb to determine overlap
    }
    verbose = 1
    pfiles1 = inv1.pfiles
    pfiles2 = inv2.pfiles
    overlap, only1, only2 = ProgressiveFile.likely_overlaps(
        pfiles1, pfiles2, thresh=thresh, verbose=verbose)

    stats = {
        'overlap': len(overlap),
        'only1': len(only1),
        'only2': len(only2),
    }
    print('stats = {}'.format(ub.repr2(stats, nl=1)))
    only2_list = sorted([p.fpath for group in only2.values() for p in group])
    print('only2_list = {}'.format(ub.repr2(only2_list, nl=1)))
    print('stats = {}'.format(ub.repr2(stats, nl=1)))


    # for pfile in inv1.pfiles:
    #     pfile._check_integrity()

    import numpy as np
    mb_read = np.array([
        pfile._parts[-1][1] / int(2 ** 20) for pfile in ub.ProgIter(inv2.pfiles)
    ])
    mb_read.max()
    mb_read.min()

    # Build all hashes up to a reasonable degree
    inv1.build_hashes(max_workers=0)

    maybe_dups = inv1.likely_duplicates(thresh=0.2)
    len(maybe_dups)

    maybe_dups = ub.sorted_keys(maybe_dups, key=lambda x: x[2])

    import networkx as nx
    import itertools as it
    # Check which directories are most likely to be duplicates
    graph = nx.Graph()

    for key, group in ub.ProgIter(maybe_dups.items(), total=len(maybe_dups), desc='build dup dir graph'):
        if key[0] == '':
            continue
        dpaths = [dirname(pfile.fpath) for pfile in group]
        for d1, d2 in it.combinations(dpaths, 2):
            graph.add_edge(d1, d2)
            edge = graph.edges[(d1, d2)]
            if 'dups' not in edge:
                edge['dups'] = 0
            edge['dups'] += 1

    edge_data = list(graph.edges(data=True))

    for dpath in ub.ProgIter(graph.nodes, desc='find lens'):
        num_children = len(os.listdir(dpath))
        graph.nodes[dpath]['num_children'] = num_children

    for d1, d2, dat in edge_data:
        nc1 = graph.nodes[d1]['num_children']
        nc2 = graph.nodes[d2]['num_children']
        ndups = dat['dups']
        dup_score = (dat['dups'] / min(nc1, nc2))
        dat['dup_score'] = dup_score
        if dup_score > 0.9:
            print('dup_score = {!r}'.format(dup_score))
            print('d1 = {!r}'.format(d1))
            print('d2 = {!r}'.format(d2))
            print('nc1 = {!r}'.format(nc1))
            print('nc2 = {!r}'.format(nc2))
            print('ndups = {!r}'.format(ndups))

    print('edge_data = {}'.format(ub.repr2(edge_data, nl=2)))

    print('maybe_dups = {}'.format(ub.repr2(maybe_dups.keys(), nl=3)))
    for key, group in maybe_dups.items():
        if key[0] == '':
            continue
        print('key = {!r}'.format(key))
        print('group = {}'.format(ub.repr2(group, nl=1)))
        for pfile in group:
            pfile.refined_to(float('inf'))

        print('key = {!r}'.format(key))

    inv2.build_hashes(max_workers=6, mode='thread')

    inv1.pfiles = [p for p in ub.ProgIter(inv1.pfiles, desc='exist check') if exists(p.fpath)]
    inv2.pfiles = [p for p in ub.ProgIter(inv2.pfiles, desc='exist check') if exists(p.fpath)]

    pfiles1 = inv1.pfiles
    pfiles2 = inv2.pfiles
    def compute_likely_overlaps(pfiles1, pfiles2):
        step_idx1 = ProgressiveFile.compatible_step_idx(pfiles1)
        step_idx2 = ProgressiveFile.compatible_step_idx(pfiles2)
        step_idx = min(step_idx1, step_idx2)
        grouped1 = ProgressiveFile.group_pfiles(pfiles1, step_idx=step_idx)
        grouped2 = ProgressiveFile.group_pfiles(pfiles2, step_idx=step_idx)

        thresh = 0.2
        verbose = 1

        # TODO: it would be nice if we didn't have to care about internal
        # deduplication when we attempt to find cross-set overlaps
        dups1 = ProgressiveFile.likely_duplicates(inv1.pfiles, thresh=thresh, verbose=verbose)
        dups2 = ProgressiveFile.likely_duplicates(inv2.pfiles, thresh=thresh, verbose=verbose)

        pfiles = inv1.pfiles + inv2.pfiles
        dups3 = ProgressiveFile.likely_duplicates(pfiles, thresh=thresh, verbose=verbose)

        only_on_inv2 = {}
        for key, group in dups3.items():
            if not any(item.fpath.startswith(inv1.root_fpath) for item in group):
                only_on_inv2[key] = group

        for p1 in inv1.pfiles:
            if 'Chase HQ 2 (JUE) [!].zip' in p1.fpath:
                break

        for p2 in inv2.pfiles:
            if 'Chase HQ 2 (JUE) [!].zip' in p2.fpath:
                break

        look = list(ub.flatten(only_on_inv2.values()))
        takealook = sorted([p.fpath for p in look])
        print('takealook = {}'.format(ub.repr2(takealook, nl=1)))

        keys1 = set(grouped1)
        keys2 = set(grouped2)

        missing_keys2 = keys2 - keys1
        missing_groups2 = ub.dict_subset(grouped2, missing_keys2)

        missing_fpaths2 = []
        for key, values in missing_groups2.items():
            print('key = {!r}'.format(key))
            print('values = {}'.format(ub.repr2(values, nl=1)))
            missing_fpaths2.extend(values)

        missing_fpaths2 = sorted([p.fpath for p in missing_fpaths2])
        print('missing_fpaths2 = {}'.format(ub.repr2(missing_fpaths2, nl=1)))
        # pass

        import xdev
        set_overlaps = xdev.set_overlaps(keys1, keys2)
        print('set_overlaps = {}'.format(ub.repr2(set_overlaps, nl=1)))
        # We want to know what files in set2 do not exist in set1

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


def _demodata_files(dpath=None, num_files=10, pool_size=3, size_pool=None, rng=0):
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

    rng = random.Random(rng)
    # Create a pool of random chunks of data
    chunksize = int(2 ** 16)
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
