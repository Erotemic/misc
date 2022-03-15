import ubelt as ub
import torch
import numpy as np
from torch.nn import functional as F


def nan_normalize(a, dim, p=2, imputation='zero', assume_nans=False):
    """
    Like torch.functional.normalize, but handles nans

    Args:
        a (Tensor): input data

        dim (int): dimension to normalize over

        p (int): type of norm

        imputation (dict | str):
            dictionary containing keys:
                method (str): either zeros or mean

            if this is a string, it becomes the method in an imputation
            dictionary created with auto defaults.

        assume_nans (bool):
            if true, skips the check if any nans exist and assume they do

    Returns:
        Tensor: normalized array

    Example:
        >>> shape = (7, 5, 3)
        >>> a = data = torch.from_numpy(np.arange(np.prod(shape)).reshape(*shape)).float()
        >>> a[0:2, 0:2, 0:2] = float('nan')
        >>> dim = 2
        >>> p = 2
        >>> nan_normalize(a, dim, p, imputation='zero')
        >>> nan_normalize(a, dim, p, imputation='mean')

        >>> # Ensure this works when no nans exist
        >>> clean_data = torch.rand(3, 2)
        >>> v1 = nan_normalize(clean_data, dim, p, imputation='mean')
        >>> v2 = nan_normalize(clean_data, dim, p, imputation='mean', assume_nans=True)
    """
    mask = torch.isnan(a)
    if assume_nans or mask.any():
        if isinstance(imputation, str):
            imputation = {
                'method': imputation
            }
        imputation_method = imputation['method']
        if imputation_method == 'zero':
            out = torch.nan_to_num(a)
        elif imputation_method == 'mean':
            out = a.clone()
            mean_dims = imputation.get('mean_dims', 'auto')
            if mean_dims == 'auto':
                mean_dims = tuple(sorted(set(range(len(a.shape))) - {dim}))
            if mean_dims is None:
                mean = a.nanmean()
                out[mask] = mean
            else:
                fill_values = a.nanmean(dim=mean_dims, keepdims=True).expand_as(out)
                out[mask] = fill_values[out]
        else:
            raise KeyError
        F.normalize(out, dim=dim, p=p, out=out)
        out[mask] = float('nan')
    else:
        out = F.normalize(out, dim=dim, p=p)
    return out

shape = (3, 5, 7)
data = torch.from_numpy(np.arange(np.prod(shape)).reshape(*shape)).float()
norm_data1 = F.normalize(data, dim=1, p=2)

nan_data1 = data.clone()
nan_data1[0:2, 0:2, 0:2] = float('nan')
norm_data1 = F.normalize(nan_data1, dim=1, p=2)

num_input_nans = torch.isnan(nan_data1).sum()
num_output_nans = torch.isnan(norm_data1).sum()
print('data =\n{}'.format(ub.repr2(data, nl=1)))
print('nan_data1 =\n{}'.format(ub.repr2(nan_data1, nl=1)))
print('norm_data1 =\n{}'.format(ub.repr2(norm_data1, nl=1)))
print('num_input_nans = {!r}'.format(num_input_nans))
print('num_output_nans = {!r}'.format(num_output_nans))


nan_data2 = data.clone()
nan_data2[:, 0:2] = float('nan')
norm_data2 = F.normalize(nan_data2, dim=1, p=2)

num_input_nans = torch.isnan(nan_data2).sum()
num_output_nans = torch.isnan(norm_data2).sum()
print('data =\n{}'.format(ub.repr2(data, nl=1)))
print('nan_data2 =\n{}'.format(ub.repr2(nan_data2, nl=1)))
print('norm_data2 =\n{}'.format(ub.repr2(norm_data2, nl=1)))
print('num_input_nans = {!r}'.format(num_input_nans))
print('num_output_nans = {!r}'.format(num_output_nans))


print('\n\n-----variant2\n\n')


nan_data1 = data.clone()
nan_data1[0:2, 0:2, 0:2] = float('nan')
norm_data1 = nan_normalize(nan_data1, dim=1, p=2)

num_input_nans = torch.isnan(nan_data1).sum()
num_output_nans = torch.isnan(norm_data1).sum()
print('data =\n{}'.format(ub.repr2(data, nl=1)))
print('nan_data1 =\n{}'.format(ub.repr2(nan_data1, nl=1)))
print('norm_data1 =\n{}'.format(ub.repr2(norm_data1, nl=1)))
print('num_input_nans = {!r}'.format(num_input_nans))
print('num_output_nans = {!r}'.format(num_output_nans))


nan_data2 = data.clone()
nan_data2[:, 0:2] = float('nan')
norm_data2 = nan_normalize(nan_data2, dim=1, p=2)

num_input_nans = torch.isnan(nan_data2).sum()
num_output_nans = torch.isnan(norm_data2).sum()
print('data =\n{}'.format(ub.repr2(data, nl=1)))
print('nan_data2 =\n{}'.format(ub.repr2(nan_data2, nl=1)))
print('norm_data2 =\n{}'.format(ub.repr2(norm_data2, nl=1)))
print('num_input_nans = {!r}'.format(num_input_nans))
print('num_output_nans = {!r}'.format(num_output_nans))
