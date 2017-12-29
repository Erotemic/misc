

import torch

parameters = [torch.autograd.Variable(torch.FloatTensor([0, 0, 0]), requires_grad=True)]
optimizer = torch.optim.SGD(parameters, lr=0.1, momentum=0.9)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, verbose=True)


def get_lrs():
    lrs = set(map(lambda group: group['lr'], optimizer.param_groups))
    return lrs


for _ in range(100):
    scheduler.step(.1)
    lrs = get_lrs()
    lr_str = ','.join(['{:.2g}'.format(lr) for lr in lrs])
    # print(lr_str)
