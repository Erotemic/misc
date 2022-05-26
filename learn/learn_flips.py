

def demo_flip_orientations():
    import ubelt as ub
    from kwcoco.demo.toypatterns import Rasters
    img = Rasters.eff()[0]

    import kwplot
    kwplot.autompl()
    kwplot.imshow(img)

    flips = [
        [],
        [0],
        [1],
        [0, 1],
    ]
    import numpy as np

    toshow = []

    for axis in flips:
        img_ = img
        img_ = np.flip(img_, axis=axis)
        for k in [0, 1, 2, 3]:
            img_ = np.rot90(img_, k=k)
            row = {'img': img_, 'label': f'rot(flip({axis}), k={k})'}
            row['params'] = [f'axis={axis}, k={k}']
            toshow.append(row)

    # for k in [0, 1, 2, 3]:
    #     img_ = img
    #     img_ = np.rot90(img_, k=k)
    #     for axis in flips:
    #         img_ = np.flip(img_, axis=axis)
    #         row = {'img': img_, 'label': f'flip(rot(k={k}), {axis})'}
    #         row['params'] = [f'k={k}, axis={axis}']
    #         toshow.append(row)

    for row in toshow:
        row['hash'] = ub.hash_data(row['img'])

    pnum_ = kwplot.PlotNums(nSubplots=len(toshow))
    groups = ub.group_items(toshow, lambda x: x['hash'])
    # Only 8 possibiliteis
    for k, group in groups.items():
        print('\n\nk = {!r}'.format(k))
        for g in group:
            print(g['params'])
            row = g
            kwplot.imshow(row['img'], pnum=pnum_(), fnum=1, title=row['label'])

    unique_fliprots = [
        {'k': 0, 'axis': []},
        {'k': 1, 'axis': []},
        {'k': 2, 'axis': []},
        {'k': 3, 'axis': []},
        {'k': 0, 'axis': [0]},
        {'k': 1, 'axis': [0]},
        {'k': 2, 'axis': [0]},
        {'k': 3, 'axis': [0]},
    ]
    s = []
    for params in unique_fliprots:
        k = params['k']
        axis = params['axis']
        img_ = np.rot90(np.flip(img, axis=axis), k=k)
        s.append(ub.hash_data(img_))

    assert len(set(s)) == len(s)
