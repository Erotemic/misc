import numpy as np
import netharn as nh
img = nh.util.imread('auc_megahack.png')

nh.util.autompl()
nh.util.imshow(img)

color = (255, 0, 255)
thresh = 150
diff = (np.abs(img.astype(np.float) - color)).astype(np.uint8)
mask = (diff.sum(axis=-1) < thresh).astype(np.float32)

nh.util.imshow(mask)

for rx, row in enumerate(mask):
    mask[rx] = row.cumsum()

for cx, col in enumerate(mask.T):
    mask.T[cx] = col.cumsum()

mask = (mask > 0).astype(np.float)

nh.util.imshow((mask > 0).astype(np.uint8) * 255)

# Clip the mask cols
mask = mask[:, ~np.all(mask.T == 0, axis=1)]


nh.util.imshow(mask)

roc_auc = mask.sum() / mask.size


diff = np.sqrt(((img.astype(np.float) - (0, 0, 0)) ** 2).sum(axis=-1))
nh.util.imshow(diff)


pixels_to_fa_count = 155 / 200000
