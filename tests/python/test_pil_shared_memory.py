
from PIL import Image
import numpy as np


# Make an zero image with a square of ones in the center
np_img = np.zeros((10, 10), dtype=np.uint8)
np_img[3:7, 3:7] = 1


"""
CLAIM:
    Conversion of an np.ndarray to a Pillow.Image shares memory.

    We will show that `pil_img` shares memory with `np_img`.
"""
# Note: pil_img.getdata() is the pil imaging core that contains the actual data
pil_img = Image.fromarray(np_img)
assert np_img.sum() == 16 and np.asarray(pil_img.getdata()).sum() == 16, (
    'np_img and pil_img should start off as the same')

"""
PROOF:
    Modifying the np_img also changes the pil_img.

    Increase np_img by 1 everywhere will increase pil_img by 1 everywhere.
"""
np_img += 1
assert np_img.sum() == 116
assert np.asarray(pil_img.getdata()).sum() == 116, (
    'the pil image data should be changed')


"""
Conversion from Pillow.Image to a np.ndarray does seem to force a copy.

Perhaps there is a different way of doing this where numpy just views the
pillow memory?
"""
new_np_img = np.asarray(pil_img.getdata())
new_np_img += 1
assert new_np_img.sum() == 216
assert np_img.sum() == 116, 'transforming the new ndarray does not change the old'


"""
However, affine transforms in pillow are not in place, so a copy would be
required either way.
"""
# note: pil uses the inverse transform
aff = np.array([[.5, 0, 2],
                [0, .5, 2]])
pil_aff_params = list(aff.ravel())
w1, h1 = np_img.shape[0:2][::-1]
imgaug = pil_img.transform((w1, h1), Image.AFFINE, pil_aff_params, resample=Image.BICUBIC)

assert np.asarray(pil_img.getdata()).sum() == 116
assert np.asarray(imgaug.getdata()).sum() == 118

# note when converting from pillow we need to re-set the shape
data = np.asarray(imgaug.getdata())
data.shape = np_img.shape
