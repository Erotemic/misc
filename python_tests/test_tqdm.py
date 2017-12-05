import tqdm
from time import sleep

for i in tqdm.trange(10, desc='1st loop'):
    for j in tqdm.trange(5, desc='2nd loop', leave=False):
        for k in tqdm.trange(100, desc='3nd loop'):
            sleep(0.01)



d = {'1': 2, '3': 4, '5': 7}

for key, val in tqdm.tqdm(d.items(), desc='foobar'):
    for i in tqdm.trange(1000, desc='inner loop'):
        sleep(0.01)
