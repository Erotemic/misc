from os.path import basename
from os.path import join
from os.path import exists
import glob
import numpy as np
import ubelt as ub
from six.moves import zip
from sklearn.model_selection._split import (_BaseKFold,)


def coco_union(dsets):
    """
    Takes the union of multiple coco datasets

    Args:
        dsets (dict): mapping from image subfolder name to the json dict
    """
    merged = ub.odict([
        ('categories', []),
        ('licenses', []),
        ('info', []),
        ('images', []),
        ('annotations', []),
    ])

    merged_cat_name_to_id = {}

    def update_ifnotin(d1, d2):
        """ copies keys from d2 that doent exist in d1 into d1 """
        for k, v in d2.items():
            if k not in d1:
                d1[k] = v
        return d1

    for key, old_dset in dsets.items():
        # hack: in our case the key is the subdir
        subdir = key

        # Create temporary indexes to map from old to new
        cat_id_map = {}
        img_id_map = {}

        # Add the licenses / info into the merged dataset
        # Licenses / info are unused in our datas, so this might not be correct
        merged['licenses'].extend(old_dset['licenses'])
        merged['info'].extend(old_dset['info'])

        # Add the categories into the merged dataset
        for old_cat in old_dset['categories']:
            new_id = merged_cat_name_to_id.get(old_cat['name'], None)
            if new_id is None:
                # The same category might exist in different datasets.
                new_id = len(merged_cat_name_to_id) + 1
                merged_cat_name_to_id[old_cat['name']] = new_id

            new_cat = ub.odict([
                ('id', new_id),
                ('name', old_cat['name']),
                ('supercategory', old_cat['supercategory']),
            ])
            update_ifnotin(new_cat, old_cat)
            cat_id_map[old_cat['id']] = new_cat['id']
            merged['categories'].append(new_cat)

        # Add the images into the merged dataset
        for old_img in old_dset['images']:
            new_img = ub.odict([
                ('id', len(merged['images']) + 1),
                ('file_name', join(subdir, old_img['file_name'])),
            ])
            # copy over other metadata
            update_ifnotin(new_img, old_img)
            img_id_map[old_img['id']] = new_img['id']
            merged['images'].append(new_img)

        # Add the annotations into the merged dataset
        for old_annot in old_dset['annotations']:
            old_cat_id = old_annot['category_id']
            old_img_id = old_annot['image_id']
            new_cat_id = cat_id_map.get(old_cat_id, None)
            new_img_id = img_id_map.get(old_img_id, None)
            if new_cat_id is None:
                continue
                print('annot {} in {} has bad category-id {}'.format(old_annot['id'], key, old_cat_id))
            if new_img_id is None:
                continue
                print('annot {} in {} has bad image-id {}'.format(old_annot['id'], key, old_img_id))
            new_annot = ub.odict([
                ('id', len(merged['annotations']) + 1),
                ('image_id', new_img_id),
                ('category_id', new_cat_id),
            ])
            update_ifnotin(new_annot, old_annot)
            merged['annotations'].append(new_annot)
    return merged


class CocoDataset(object):
    """
    Notation:
        aid - Annotation ID
        gid - imaGe ID
        cid - Category ID
    """
    def __init__(self, data, img_root='.', autobuild=True):
        self.dataset = data
        self.img_root = img_root

        if autobuild:
            self._build_index()

    def _build_index(self):
        """ build reverse indexes """
        # create index
        anns, cats, imgs = {}, {}, {}
        gid_to_aids = ub.ddict(list)
        cid_to_gids = ub.ddict(list)
        cid_to_aids = ub.ddict(list)

        for ann in self.dataset.get('annotations', []):
            gid_to_aids[ann['image_id']].append(ann['id'])
            anns[ann['id']] = ann

        for img in self.dataset.get('images', []):
            imgs[img['id']] = img

        for cat in self.dataset.get('categories', []):
            cats[cat['id']] = cat

        if anns and cats:
            for ann in self.dataset['annotations']:
                cid_to_gids[ann['category_id']].append(ann['image_id'])

        for cat, gids in cid_to_gids.items():
            aids = [aid for gid in gids for aid in gid_to_aids[gid]]
            cid_to_aids[cat] = aids

        # create class members
        self.gid_to_aids = gid_to_aids
        self.cid_to_gids = cid_to_gids
        self.cid_to_aids = cid_to_aids
        self.anns = anns
        self.imgs = imgs
        self.cats = cats

    def subset(self, sub_gids):
        new_dataset = ub.odict([(k, []) for k in self.dataset])
        new_dataset['categories'] = self.dataset['categories']
        new_dataset['info'] = self.dataset['info']
        new_dataset['licenses'] = self.dataset['licenses']

        sub_aids = sorted([aid for gid in sub_gids
                           for aid in self.gid_to_aids[gid]])
        new_dataset['annotations'] = list(ub.take(self.anns, sub_aids))
        new_dataset['images'] = list(ub.take(self.imgs, sub_gids))
        sub_dset = CocoDataset(new_dataset)
        return sub_dset

    def run_fixes(self):
        for ann in self.anns.values():
            # Note standard coco bbox is [x,y,width,height]
            if 'roi_shape' not in ann:
                ann['roi_shape'] = 'bounding_box'

            if ann['roi_shape'] == 'boundingBox':
                x1, y1, x2, y2 = ann['bbox']

                assert x2 >= x1
                assert y2 >= y1

                w = x2 - x1
                h = y2 - y1
                ann['bbox'] = [x1, y1, w, h]
                ann['roi_shape'] = 'bounding_box'

            if ann['roi_shape'] == 'point' and 'point' not in ann:
                x, y, w, h = ann['bbox']
                ann['point'] = (x, y)

            if ann['roi_shape'] == 'line' and 'line' not in ann:
                # hack in a decent bounding box to fix the roi.
                # Assume the line is the diameter of an enscribed circle
                x1, y1, x2, y2 = ann['bbox']
                xc = (x1 + x2) / 2
                yc = (y1 + y2) / 2
                length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                bbox = [(xc - length / 2), (yc - length / 2), length, length]
                ann['bbox'] = bbox
                ann['line'] = [(x1, y1), (x2, y2)]

    def _ensure_imgsize(self):
        from PIL import Image
        for img in ub.ProgIter(list(self.imgs.values())):
            gpath = join(self.img_root, img['file_name'])
            if 'width' not in img:
                pil_img = Image.open(gpath)
                w, h = pil_img.size
                pil_img.close()
                img['width'] = w
                img['height'] = h

    def show_annotation(self, primary_aid=None, gid=None):
        import matplotlib as mpl
        from matplotlib import pyplot as plt
        import cv2

        if gid is None:
            primary_ann = self.anns[primary_aid]
            gid = primary_ann['image_id']

        img = self.imgs[gid]
        aids = self.gid_to_aids[img['id']]

        # Show image
        gpath = join(self.img_root, img['file_name'])
        np_img = cv2.imread(gpath)
        np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        plt.imshow(np_img)
        ax = plt.gca()

        # Show all annotations inside it
        segments = []
        points = []
        rects = []
        for aid in aids:
            ann = self.anns[aid]
            # Note standard coco bbox is [x,y,width,height]
            [x, y, w, h] = ann['bbox']

            catname = self.cats[ann['category_id']]['name']
            textkw = {
                'horizontalalignment': 'left',
                'verticalalignment': 'top',
                'backgroundcolor': (0, 0, 0, .3),
                'color': 'white',
                'fontproperties': mpl.font_manager.FontProperties(
                    size=6, family='monospace'),
            }
            ax.text(x, y, catname, **textkw)

            color = 'orange' if aid == primary_aid else 'blue'
            rect = mpl.patches.Rectangle((x, y), w, h, facecolor='none',
                                         edgecolor=color)
            rects.append(rect)
            if 'line' in ann:
                segments.append(ann['line'])
            if 'point' in ann:
                points.append(ann['point'])

        if segments:
            line_col = mpl.collections.LineCollection(segments, 2, color='b')
            ax.add_collection(line_col)

        rect_col = mpl.collections.PatchCollection(rects, match_original=True)
        ax.add_collection(rect_col)
        if points:
            print('points = {!r}'.format(points))
            xs, ys = list(zip(*points))
            ax.plot(xs, ys, 'bo')


# from sklearn.utils.fixes import bincount
bincount = np.bincount


class StratifiedGroupKFold(_BaseKFold):
    """Stratified K-Folds cross-validator with Grouping

    Provides train/test indices to split data in train/test sets.

    This cross-validation object is a variation of GroupKFold that returns
    stratified folds. The folds are made by preserving the percentage of
    samples for each class.

    Read more in the :ref:`User Guide <cross_validation>`.

    Parameters
    ----------
    n_splits : int, default=3
        Number of folds. Must be at least 2.
    """

    def __init__(self, n_splits=3, shuffle=False, random_state=None):
        super(StratifiedGroupKFold, self).__init__(n_splits, shuffle, random_state)

    def _make_test_folds(self, X, y=None, groups=None):
        """
        Args:
            self (?):
            X (ndarray):  data
            y (ndarray):  labels(default = None)
            groups (None): (default = None)

        CommandLine:
            python -m ibeis.algo.verif.sklearn_utils _make_test_folds

        Example:
            >>> rng = np.random.RandomState(0)
            >>> groups = [1, 1, 3, 4, 2, 2, 7, 8, 8]
            >>> y      = [1, 1, 1, 1, 2, 2, 2, 3, 3]
            >>> X = np.empty((len(y), 0))
            >>> self = StratifiedGroupKFold(random_state=rng)
            >>> skf_list = list(self.split(X=X, y=y, groups=groups))
        """
        n_splits = self.n_splits
        y = np.asarray(y)
        n_samples = y.shape[0]

        unique_y, y_inversed = np.unique(y, return_inverse=True)
        n_classes = max(unique_y) + 1
        group_to_idxs = ub.group_items(range(len(groups)), groups)
        # unique_groups = list(group_to_idxs.keys())
        group_idxs = list(group_to_idxs.values())
        grouped_y = [y.take(idxs) for idxs in group_idxs]
        grouped_y_counts = np.array([
            bincount(y_, minlength=n_classes) for y_ in grouped_y])

        target_freq = grouped_y_counts.sum(axis=0)
        target_ratio = target_freq / target_freq.sum()

        # Greedilly choose the split assignment that minimizes the local
        # * squared differences in target from actual frequencies
        # * and best equalizes the number of items per fold
        # Distribute groups with most members first
        split_freq = np.zeros((n_splits, n_classes))
        # split_ratios = split_freq / split_freq.sum(axis=1)
        split_ratios = np.ones(split_freq.shape) / split_freq.shape[1]
        split_diffs = ((split_freq - target_ratio) ** 2).sum(axis=1)
        sortx = np.argsort(grouped_y_counts.sum(axis=1))[::-1]
        grouped_splitx = []
        for count, group_idx in enumerate(sortx):
            group_freq = grouped_y_counts[group_idx]
            cand_freq = split_freq + group_freq
            cand_ratio = cand_freq / cand_freq.sum(axis=1)[:, None]
            cand_diffs = ((cand_ratio - target_ratio) ** 2).sum(axis=1)
            # Compute loss
            losses = []
            other_diffs = np.array([
                sum(split_diffs[x + 1:]) + sum(split_diffs[:x])
                for x in range(n_splits)
            ])
            # penalize unbalanced splits
            ratio_loss = other_diffs + cand_diffs
            # penalize heavy splits
            freq_loss = split_freq.sum(axis=1)
            denom = freq_loss.sum()
            if denom == 0:
                freq_loss = freq_loss * 0
            else:
                freq_loss = freq_loss / denom
            losses = ratio_loss + freq_loss
            #-------
            splitx = np.argmin(losses)
            split_freq[splitx] = cand_freq[splitx]
            split_ratios[splitx] = cand_ratio[splitx]
            split_diffs[splitx] = cand_diffs[splitx]
            grouped_splitx.append(splitx)

        test_folds = np.empty(n_samples, dtype=np.int)
        for group_idx, splitx in zip(sortx, grouped_splitx):
            idxs = group_idxs[group_idx]
            test_folds[idxs] = splitx

        return test_folds

    def _iter_test_masks(self, X, y=None, groups=None):
        test_folds = self._make_test_folds(X, y, groups)
        for i in range(self.n_splits):
            yield test_folds == i

    def split(self, X, y, groups=None):
        """Generate indices to split data into training and test set.
        """
        from sklearn.utils.validation import check_array
        y = check_array(y, ensure_2d=False, dtype=None)
        return super(StratifiedGroupKFold, self).split(X, y, groups)


def make_baseline_truthfiles():
    work_dir = ub.truepath('~/work/viame-challenge-2018')
    data_dir = ub.truepath('~/data')

    challenge_data_dir = join(data_dir, 'viame-challenge-2018')
    challenge_work_dir = join(work_dir, 'viame-challenge-2018')

    ub.ensuredir(challenge_work_dir)

    img_root = join(challenge_data_dir, 'phase0-imagery')
    annot_dir = join(challenge_data_dir, 'phase0-annotations')
    fpaths = list(glob.glob(join(annot_dir, '*.json')))
    # ignore the non-bounding box nwfsc and afsc datasets for now

    # exclude = ('nwfsc', 'afsc', 'mouss', 'habcam')
    # fpaths = [p for p in fpaths if not basename(p).startswith(exclude)]

    import json
    dsets = ub.odict()
    for fpath in fpaths:
        key = basename(fpath).split('.')[0]
        dsets[key] = json.load(open(fpath, 'r'))

    print('Merging')
    merged = coco_union(dsets)

    merged_fpath = join(challenge_work_dir, 'phase0-merged.mscoco.json')
    with open(merged_fpath, 'w') as fp:
        json.dump(merged, fp, indent=4)

    import copy
    self = CocoDataset(copy.deepcopy(merged), img_root=img_root, autobuild=False)
    self._build_index()
    self.run_fixes()

    if True:
        print('Fixing')
        # remove all point annotations
        to_remove = []
        for ann in self.dataset['annotations']:
            if ann['roi_shape'] == 'point':
                to_remove.append(ann)
        for ann in to_remove:
            self.dataset['annotations'].remove(ann)
        self._build_index()

        # remove empty images
        to_remove = []
        for gid, aids in self.gid_to_aids.items():
            if not aids:
                to_remove.append(self.imgs[gid])
        for img in to_remove:
            self.dataset['images'].remove(img)
        self._build_index()

    # for gid, aids in self.gid_to_aids.items():
    #     for ann in ub.take(self.anns, ann)

    catname_to_nannots = ub.map_keys(lambda x: self.cats[x]['name'],
                                     ub.map_vals(len, self.cid_to_aids))
    catname_to_nannots = ub.odict(sorted(catname_to_nannots.items(),
                                         key=lambda kv: kv[1]))
    print(ub.repr2(catname_to_nannots))

    if False:
        # aid = list(self.anns.values())[0]['id']
        # self.show_annotation(aid)
        gids = sorted([gid for gid, aids in self.gid_to_aids.items() if aids])
        # import utool as ut
        # for gid in ut.InteractiveIter(gids):
        for gid in gids:
            from matplotlib import pyplot as plt
            fig = plt.figure(1)
            fig.clf()
            self.show_annotation(gid=gid)
            fig.canvas.draw()

        for ann in self.anns.values():
            primary_aid = ann['id']
            print('primary_aid = {!r}'.format(primary_aid))
            print(len(self.gid_to_aids[ann['image_id']]))

            if 'roi_shape' not in ann:
                ann['roi_shape'] = 'bounding_box'

            if ann['roi_shape'] == 'boundingBox':
                pass

            if ann['roi_shape'] == 'point':
                primary_aid = ann['id']
                print('primary_aid = {!r}'.format(primary_aid))
                print(len(self.gid_to_aids[ann['image_id']]))
                break

    # Split into train / test  set
    print('Splitting')
    skf = StratifiedGroupKFold(n_splits=2)
    groups = [ann['image_id'] for ann in self.anns.values()]
    y = [ann['category_id'] for ann in self.anns.values()]
    X = [ann['id'] for ann in self.anns.values()]
    split = list(skf.split(X=X, y=y, groups=groups))[0]
    train_idx, test_idx = split

    print('Taking subsets')
    aid_to_gid = {aid: ann['image_id'] for aid, ann in self.anns.items()}
    train_aids = list(ub.take(X, train_idx))
    test_aids = list(ub.take(X, test_idx))
    train_gids = sorted(set(ub.take(aid_to_gid, train_aids)))
    test_gids = sorted(set(ub.take(aid_to_gid, test_aids)))

    train_dset = self.subset(train_gids)
    test_dset = self.subset(test_gids)

    with open(join(challenge_work_dir, 'phase0-merged-train.mscoco.json'), 'w') as fp:
        json.dump(train_dset.dataset, fp, indent=4)

    with open(join(challenge_work_dir, 'phase0-merged-test.mscoco.json'), 'w') as fp:
        json.dump(test_dset.dataset, fp, indent=4)

    # Make a detectron yaml file
    config_text = ub.codeblock(
        """
        MODEL:
          TYPE: generalized_rcnn
          CONV_BODY: ResNet.add_ResNet50_conv4_body
          NUM_CLASSES: {num_classes}
          FASTER_RCNN: True
        NUM_GPUS: 1
        SOLVER:
          WEIGHT_DECAY: 0.0001
          LR_POLICY: steps_with_decay
          BASE_LR: 0.01
          GAMMA: 0.1
          # 1x schedule (note TRAIN.IMS_PER_BATCH: 1)
          MAX_ITER: 180000
          STEPS: [0, 120000, 160000]
        RPN:
          SIZES: (32, 64, 128, 256, 512)
        FAST_RCNN:
          ROI_BOX_HEAD: ResNet.add_ResNet_roi_conv5_head
          ROI_XFORM_METHOD: RoIAlign
        TRAIN:
          WEIGHTS: https://s3-us-west-2.amazonaws.com/detectron/ImageNetPretrained/MSRA/R-50.pkl
          DATASETS: ('phase0-merged-train.mscoco.json',)
          SCALES: (800,)
          MAX_SIZE: 1333
          IMS_PER_BATCH: 1
          BATCH_SIZE_PER_IM: 512
        TEST:
          DATASETS: ('phase0-merged-test.mscoco.json',)
          SCALES: (800,)
          MAX_SIZE: 1333
          NMS: 0.5
          RPN_PRE_NMS_TOP_N: 6000
          RPN_POST_NMS_TOP_N: 1000
        OUTPUT_DIR: /work/viame-challenge-2018/output
        """)
    config_text = config_text.format(
        num_classes=len(self.cats)
    )
    ub.writeto(join(work_dir, 'phase0.yaml'), config_text)

    # nvidia-docker run -v $WORK_DIR:/work $DATA_DIR:/data -it detectron:c2-cuda9-cudnn7 bash

    # self = coco.COCO(merged_fpath)
    # cats = coco.loadCats(coco.getCatIds())
    # for cat in cats:
    #     imgs = coco.catToImgs[cat['id']]
    #     if len(imgs) == 0:
    #         print(cat)


def parse_fish_data():
    annot_dir = ub.truepath('~/data/viame-challenge-2018/phase0-annotations')
    assert exists(annot_dir)
    for fpath in glob.glob(join(annot_dir, '*.json')):
        # ub.cmd('sed -i "s/roi_category/category_id/g" {}'.format(fpath))
        # self = coco.COCO(fpath)
        break
        # try:
        # except Exception:
        #     print(ub.color_text('ERROR: {}'.format(fpath), 'blue'))
        # else:
        #     print(ub.color_text('SUCCESS: {}'.format(fpath), 'blue'))
