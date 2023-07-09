class Foo:
    def __getitem__(self, arg):
        print(f'arg={arg!r}')
        return arg


self = Foo()

self[1]
self[1, 2, 3]
self[[1, 2, 3]]
self[...]
self[..., ]
self[:, :, :]
self[:, [1, 2, 3]]
self[tuple([slice(None), [1, 2, 3]])]

self[..., None, ...]
