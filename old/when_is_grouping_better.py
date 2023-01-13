"""
Demo of when grouping is better than indexing
"""


def main():
    """
    Say we have a produces an assignment between true detections within images
    and some set of predictions.
    """
    import numpy as np
    import ubelt as ub

    # Create demo detection metrics
    from kwcoco.metrics import DetectionMetrics
    dmet = DetectionMetrics.demo(
        nimgs=1000, nboxes=(0, 10), n_fp=(0, 10), n_fn=(0, 10))

    # We might have some sort of mapping between images and the predicted and
    # true boxes (note gid means imaGe id).
    gid_to_true = dmet.gid_to_true_dets
    gid_to_pred = dmet.gid_to_pred_dets
    print('gid_to_true = {}'.format(str(gid_to_true)[0:100] + ' ...'))
    print('gid_to_pred = {}'.format(str(gid_to_pred)[0:100] + ' ...'))
    """
    gid_to_true = {0: <Detections(5) at 0x7fe08c335a10>, 1: <Detections(5) at 0x7fe08c3359d0>, 2: <Detections(8) at 0x ...
    gid_to_pred = {0: <Detections(2) at 0x7fe08c335990>, 1: <Detections(6) at 0x7fe08c335dd0>, 2: <Detections(13) at 0 ...
    """

    # Each detection might have data like this
    print('gid_to_true[0].data = {}'.format(ub.repr2(gid_to_true[0].data, nl=1)))
    """
    gid_to_true[0].data = {
        'boxes': <Boxes(cxywh,
                     array([[74.07547  , 61.581673 , 24.438194 , 47.287003 ],
                            [28.509544 , 26.718906 ,  3.487833 , 43.095215 ],
                            [60.247677 , 65.802795 , 42.938393 , 36.610165 ],
                            [35.281883 , 80.26636  ,  4.0845375, 31.898323 ],
                            [30.69794  , 83.549904 , 34.32573  ,  7.9176483]], dtype=float32))>,
        'class_idxs': np.array([1, 1, 1, 1, 1], dtype=np.int64),
        'weights': np.array([1, 1, 1, 1, 1], dtype=np.int32),
    }
    """

    # we can compute an association between each box and get a flat table
    table = dmet.confusion_vectors().data

    # The table of values might look something like this.
    # Again, note the gids correspond to imaGe ids
    # txs correspond to indexes of true detections in that image
    # pxs correspond to indexes of predicted detections in that image
    # A -1 in an index value means the row is unassociated
    print(table.pandas()[['gid', 'txs', 'pxs']])
    """
          gid  txs  pxs
    0       0    3    0
    1       0    4    1
    2       0    0   -1
    3       0    1   -1
    4       0    2   -1
    ...   ...  ...  ...
    9881  999   -1    1
    9882  999   -1    3
    9883  999   -1    2
    9884  999    0   -1
    9885  999    1   -1

    """

    # Say we need to know some attribute (e.g. the bounding boxes) for all of
    # the true associations, but the table is already flattened. (multiple
    # duplicate gids per row). How do we access that data?

    # We could use a list comprehension and lookup the Detections object for
    # that image and then look up the index within the image:
    data_attr_v1 = np.array([
        [-1] * 4 if tx == -1 else gid_to_true[gid].data['boxes'].data[tx]
        for gid, tx in zip(table['gid'], table['txs'])
    ])

    # But that means we are accessing the __getitem__ of gid_to_true a lot
    # Is there a better way?

    # Yes, we can group the table by image id.
    import kwarray
    data_attr_v2 = np.full((len(table), 4), fill_value=-1.0)
    unique_gids, groupxs = kwarray.group_indices(table['gid'])
    for gid, groupxs in zip(unique_gids, groupxs):
        true_det = gid_to_true[gid]
        image_txs = table['txs'][groupxs]
        valid_flags = image_txs != -1
        valid_txs = image_txs[valid_flags]
        valid_groupxs = groupxs[valid_flags]
        valid_attr = true_det.data['boxes'].data[valid_txs]
        data_attr_v2[valid_groupxs] = valid_attr

    # We can see both codeblocks are the same, but which is faster
    assert np.all(data_attr_v2 == data_attr_v1)

    import timerit
    ti = timerit.Timerit(50, bestof=10, verbose=2)
    for timer in ti.reset('list-comprehension'):
        with timer:
            data_attr_v1 = np.array([
                [-1] * 4 if tx == -1 else gid_to_true[gid].data['boxes'].data[tx]
                for gid, tx in zip(table['gid'], table['txs'])
            ])

    for timer in ti.reset('grouping'):
        with timer:
            data_attr_v2 = np.full((len(table), 4), fill_value=-1.0)
            unique_gids, groupxs = kwarray.group_indices(table['gid'])
            for gid, groupxs in zip(unique_gids, groupxs):
                true_det = gid_to_true[gid]
                image_txs = table['txs'][groupxs]
                valid_flags = image_txs != -1
                valid_txs = image_txs[valid_flags]
                valid_groupxs = groupxs[valid_flags]
                valid_attr = true_det.data['boxes'].data[valid_txs]
                data_attr_v2[valid_groupxs] = valid_attr

    # The grouping method is 3x faster, even though its longer!  It lets you
    # vectorize more operations and ultimately perform fewer python ops. So
    # give grouping a try in your data if you have flat tables that need to be
    # unflattened.
