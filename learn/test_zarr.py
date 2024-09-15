

def basic_zarr():
    import zarr
    import numpy as np
    array1 = (np.random.rand(32, 32)).astype(np.float32)
    array2 = (np.random.rand(32, 32) * 255).astype(np.uint8)
    array3 = ['foo', 'bar', 'baz']

    fpath = 'test.zarr'
    zarr.save(fpath, **{
        'array1': array1,
        'array2': array2,
        'array3': array3
    })

    loaded = zarr.load(fpath)
    loaded['array1']
    loaded['array2']
    loaded['array3']


def demo_zarr_dataset():
    import kwarray
    import zarr
    import numpy as np
    rng = kwarray.ensure_rng(0)

    # Create a pretend dataset
    classes = ['class_a', 'class_b', 'class_c']

    def generate_pretend_batch_item():
        im_thwc = rng.rand(1, 32, 32, 3)
        class_idxs = rng.randint(0, len(classes), size=1)
        class_ohe = kwarray.one_hot_embedding(class_idxs, len(classes)).astype(np.uint8)
        item = {
            'im_thwc': im_thwc,
            'nonlocal_class_ohe': class_ohe,
        }
        return item

    num_batch_items = 10

    # Create a zarr directory that we wil dynamically build up
    import ubelt as ub
    root_path = ub.Path('data/root.zarr')
    root_path.delete()
    root = zarr.open(root_path, mode='w')

    # Create two top-level groups one for metadata and another that
    # will contain each batch item.
    meta = root.create_group('metadata')
    batches = root.create_group('batches')

    # Write the common metadata at the top level
    zarr.save(store=meta.store, path=meta.path, classes=classes)

    # For each batch item write it out separately

    for batch_idx in range(num_batch_items):
        batch_name = f'batch_{batch_idx:03d}'
        batch_item = generate_pretend_batch_item()
        batch = batches.create_group(batch_name, overwrite=True)
        zarr.save(store=batch.store, path=batch.path, **batch_item)

    # Load and iterate over the saved zarr file
    import torch
    # The __init__part of the dataset, which should be very fast
    # because a zarr open should be lazy, and we just need to enumerate the
    # names of the batches without actually accessing any of them
    recon_root = zarr.open(root_path, mode='r')
    batches = recon_root['batches']
    # We can read the metadata in the init as it should be small
    classes = recon_root['metadata']['classes'][:]
    available_batches = list(batches.keys())
    dataset_length = len(available_batches)

    for index in range(dataset_length):
        # __getitem___ part of the dataset, where we lookup an item based on an
        # integer index.
        batch_name = available_batches[index]
        zarr_batch_item = batches[batch_name]
        batch_item = {
            key: torch.from_numpy(value[:])
            for key, value in zarr_batch_item.items()
        }
