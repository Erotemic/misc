from os.path import basename
from os.path import join
from os.path import exists
import glob
import numpy as np
import ubelt as ub

ub.codeblock(
    """
    MODEL:
      TYPE: generalized_rcnn
      CONV_BODY: ResNet.add_ResNet50_conv4_body
      NUM_CLASSES: 81
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
      DATASETS: ('coco_2014_train', 'coco_2014_valminusminival')
      SCALES: (800,)
      MAX_SIZE: 1333
      IMS_PER_BATCH: 1
      BATCH_SIZE_PER_IM: 512
    TEST:
      DATASETS: ('coco_2014_minival',)
      SCALES: (800,)
      MAX_SIZE: 1333
      NMS: 0.5
      RPN_PRE_NMS_TOP_N: 6000
      RPN_POST_NMS_TOP_N: 1000
    OUTPUT_DIR: $WORK_DIR/viame-challenge-2018/output
    """)


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
        np_img = cv2.imread(join(self.img_root, img['file_name']))
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
            ax.plot(*list(zip(*points)), 'bo')


def make_baseline_truthfiles():
    challenge_dir = ub.truepath('~/data/viame-challenge-2018')
    img_root = join(challenge_dir, 'phase0-imagery')
    annot_dir = ub.truepath('~/data/viame-challenge-2018/phase0-annotations')
    fpaths = list(glob.glob(join(annot_dir, '*.json')))
    # ignore the non-bounding box nwfsc and afsc datasets for now

    exclude = (
        'nwfsc',
        # 'afsc',
        'mouss',
        'habcam')
    fpaths = [p for p in fpaths if not basename(p).startswith(exclude)]

    import json
    dsets = ub.odict()
    for fpath in fpaths:
        key = basename(fpath).split('.')[0]
        dsets[key] = json.load(open(fpath, 'r'))

    merged = coco_union(dsets)

    merged_fpath = join(challenge_dir, 'phase0-merged.mscoco.json')
    with open(merged_fpath, 'w') as fp:
        json.dump(merged, fp, indent=4)

    import copy
    self = CocoDataset(copy.deepcopy(merged), img_root=img_root)
    self.run_fixes()

    catname_to_nannots = ub.map_keys(lambda x: self.cats[x]['name'],
                                     ub.map_vals(len, self.cid_to_aids))
    catname_to_nannots = ub.odict(sorted(catname_to_nannots.items(),
                                         key=lambda kv: kv[1]))
    print(ub.repr2(catname_to_nannots))

    aid = list(self.anns.values())[0]['id']
    self.show_annotation(aid)

    import utool as ut
    gids = sorted([gid for gid, aids in self.gid_to_aids.items() if aids])
    for gid in ut.InteractiveIter(gids):
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
