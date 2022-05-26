"""
Test numpy batch matrix multiplication
"""
import numpy as np
import timerit

B = 1245848  # batch size
D = 3  # dimensionality

Ri = np.random.rand(D, D, B)
pts_Rw = np.random.rand(D, B)

result = np.matmul(Ri, pts_Rw[:, None], axes=[(0, 1), (0, 1), (0, 1)])

ti = timerit.Timerit(1000, bestof=1, verbose=2)

for timer in ti.reset('mm-transpose'):
    with timer:
        result1 = np.matmul(Ri.transpose(2, 0, 1), pts_Rw.transpose(1, 0)[..., None])

for timer in ti.reset('mm-axes'):
    with timer:
        result2 = np.matmul(Ri, pts_Rw[:, None, :], axes=[(0, 1), (0, 1), (0, 1)])

for timer in ti.reset('mm-einsum'):
    with timer:
        result3 = np.einsum("ijb, jkb -> ikb", Ri, pts_Rw[:, None, :])

for timer in ti.reset('mm-einsum-v2'):
    with timer:
        result4 = np.einsum("ijb, jb -> ib", Ri, pts_Rw)

assert np.allclose(result1.transpose(1, 2, 0), result2)
assert np.allclose(result2, result3)
assert np.allclose(result2[:, 0, :], result4)
assert np.allclose(result2[:, 0, :], np.einsum("ijb, jb -> ib", Ri, pts_Rw))


# Add in torch for comparison

import torch  # NOQA

for timer in ti.reset('torch-bmm-cpu'):
    with timer:
        result5 = torch.bmm(
            torch.from_numpy(Ri.transpose(2, 0, 1)),
            torch.from_numpy(pts_Rw.transpose(1, 0)[..., None])
        ).numpy()

device = 1
for timer in ti.reset('torch-bmm-gpu'):
    with timer:
        result6 = torch.bmm(
            torch.from_numpy(Ri.transpose(2, 0, 1)).to(device),
            torch.from_numpy(pts_Rw.transpose(1, 0)[..., None]).to(device)
        ).cpu().numpy()

assert np.allclose(result1, result5)
assert np.allclose(result1, result6)
