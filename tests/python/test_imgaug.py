import numpy as np
from imgaug import augmenters as iaa

frames = np.zeros((5, 2, 2))
frames[:, 0, 0] = 1
frames[:, 0, 1] = 2
frames[:, 1, 0] = 3
frames[:, 1, 1] = 4


aug = iaa.Fliplr(0.5)
aug.augment_images(frames)
aug.augment_image(frames[0])

det = aug.to_deterministic()
det.augment_images(frames)

det.augment_image(frames[0].astype(np.uint8))
det.augment_image(frames[0].astype(np.float32))
det.augment_image(frames[0].astype(np.uint16))


aug = iaa.Sequential([
    # iaa.Sometimes(0.5, iaa.AdditiveGaussianNoise(scale=(0, 0.01 * 255))),
    iaa.Sometimes(0.9, iaa.Dropout(p=(0, .5))),
    iaa.Sometimes(0.9, iaa.GaussianBlur(sigma=(0, 0.1))),
    # iaa.Sometimes(0.5, iaa.Salt(p=(0, 0.001))),
    # iaa.Sometimes(0.5, iaa.Pepper(p=(0, 0.001))),
], random_order=True).to_deterministic()

aug.augment_images(frames)
aug.reseed(100, deterministic_too=True)
aug.augment_images(frames)
aug.reseed(101, deterministic_too=True)
aug.augment_images(frames)

rng = np.random.RandomState(0)
aug.reseed(rng, deterministic_too=True)
print(aug.augment_images(frames).ravel())
print('---')
aug.reseed(rng, deterministic_too=True)
print(aug.augment_images(frames).ravel())


rng = np.random.RandomState(0)
aug = iaa.Sequential([
    iaa.Fliplr(0.5),
    iaa.Flipud(0.5),
    iaa.ContrastNormalization((0.75, 1.5)),
    iaa.Affine(
        scale={"x": (0.9, 1.1), "y": (0.9, 1.1)},
        rotate=(-5, 5),
        shear=(-2, 2),
        order=3,
    ),
    iaa.PiecewiseAffine(scale=(0.01, 0.05)),
], random_order=True)
aug.reseed(rng, deterministic_too=True)
print(aug.augment_images(frames).ravel())


aug = aug.to_deterministic()
aug.reseed(rng, deterministic_too=True)
print(np.array([aug.augment_image(f) for f in frames]).ravel())
print(aug.augment_images(frames).ravel())


aug.reseed(rng, deterministic_too=True)
print(aug.augment_images(frames).ravel())
print('---')
aug.reseed(rng, deterministic_too=True)
print(aug.augment_images(frames).ravel())


import numpy as np
from imgaug import augmenters as iaa
rng = np.random.RandomState(10)
data_f = rng.rand(16, 16, 16).astype(np.float32)
data_u = (data_f * 255).astype(np.uint8)
auger = iaa.GaussianBlur(sigma=(0, 0.001))
aug_f = auger.augment_images(data_f)
aug_u = auger.augment_images(data_u)
pt.imshow(data[0], fnum=2, pnum=(1, 3, 1))
pt.imshow(aug_f[0], fnum=2, pnum=(1, 3, 2))
pt.imshow(aug_u[0], fnum=2, pnum=(1, 3, 3))


import numpy as np
from imgaug import augmenters as iaa
rng = np.random.RandomState(10)
data_f = rng.rand(16, 16, 16).astype(np.float32)
data_u = (data_f * 255).astype(np.uint8)
auger = iaa.Dropout(p=(0, .1))
aug_f = auger.augment_images(data_f)
aug_u = auger.augment_images(data_u)
pt.imshow(data[0], fnum=2, pnum=(1, 3, 1))
pt.imshow(aug_f[0], fnum=2, pnum=(1, 3, 2))
pt.imshow(aug_u[0], fnum=2, pnum=(1, 3, 3))

import numpy as np
from imgaug import augmenters as iaa
rng = np.random.RandomState(10)
data_f = rng.rand(16, 16, 16).astype(np.float32)
data_u = (data_f * 255).astype(np.uint8)
auger = iaa.Fliplr(1, deterministic=True)
aug_f = auger.augment_images(data_f)
aug_u = auger.augment_images(data_u)
pt.imshow(data[0], fnum=2, pnum=(1, 3, 1))
pt.imshow(aug_f[0], fnum=2, pnum=(1, 3, 2))
pt.imshow(aug_u[0], fnum=2, pnum=(1, 3, 3))

import numpy as np
from imgaug import augmenters as iaa
rng = np.random.RandomState(10)
data_f = rng.rand(16, 16, 16).astype(np.float32)
data_u = (data_f * 255).astype(np.uint8)
auger = iaa.Flipud(1, deterministic=True)
aug_f = auger.augment_images(data_f)
aug_u = auger.augment_images(data_u)
pt.imshow(data[0], fnum=2, pnum=(1, 3, 1))
pt.imshow(aug_f[0], fnum=2, pnum=(1, 3, 2))
pt.imshow(aug_u[0], fnum=2, pnum=(1, 3, 3))


from imgaug import augmenters as iaa
import numpy as np
def test_auger(auger):
    rng = np.random.RandomState(10)
    data_f = rng.rand(16, 16, 16).astype(np.float32)
    data_u = (data_f * 255).astype(np.uint8)
    aug_f = auger.augment_images(data_f)
    aug_u = auger.augment_images(data_u)
    # pt.imshow(data_f[0], fnum=2, pnum=(1, 3, 1))
    # pt.imshow(aug_f[0], fnum=2, pnum=(1, 3, 2))
    # pt.imshow(aug_u[0], fnum=2, pnum=(1, 3, 3))
    return data_f, data_u, aug_f, aug_u

seq = iaa.Sometimes(0.9999, iaa.GaussianBlur(sigma=(0, 0.001)))
data_f, data_u, aug_f, aug_u = test_auger(seq)
print(aug_f)
print(aug_u)


seq = iaa.Sequential([
    # iaa.Sometimes(0.5, iaa.AdditiveGaussianNoise(scale=(0, 0.01 * 255))),
    # iaa.Sometimes(0.5, iaa.Dropout(p=(0, .1))),
    iaa.Sometimes(0.9, iaa.GaussianBlur(sigma=(0, 0.001))),
    # iaa.Sometimes(0.5, iaa.Salt(p=(0, 0.001))),
    # iaa.Sometimes(0.5, iaa.Pepper(p=(0, 0.001))),
], random_order=True, random_state=dset.rng).to_deterministic()

seq = iaa.GaussianBlur(sigma=(0, 0.001))
seq = iaa.Sometimes(0.9, iaa.GaussianBlur(sigma=(0, 0.001)))
data_f, data_u, aug_f, aug_u = test_auger(seq)




>>> import numpy as np
>>> from imgaug import augmenters as iaa
>>> rng = np.random.RandomState(10)
>>> data = rng.randint(0, 255, size=(3, 5, 5)).astype(np.uint8)
>>> x = iaa.Dropout(p=(0, .1))
>>> print('Works correctly')
>>> print(x.augment_images(data))
>>>
>>> print('Returns almost all zeros')
>>> print(x.augment_images(data.astype(np.float32) / 255))

# p2 = iaa.arithmetic.Binomial(.9)
# x = iaa.MultiplyElementwise(


data = np.zeros((5, 2, 2), dtype=np.float32)
data[:, 0, 0] = .25
data[:, 0, 1] = .5
data[:, 1, 0] = .75
data[:, 1, 1] = 1

# x = iaa.Fliplr(0.5)
x = iaa.ContrastNormalization(.5)
x.augment_images((data * 255).astype(np.uint8))
x.augment_images(data)
