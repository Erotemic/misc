import ubelt as ub
import sys
import time
from datetime import timedelta


timer = ub.Timer().tic()

print('Welcome to stopwatch')

try:
    while True:
        total_sec = timer.toc()
        total_min, sec_rem = divmod(total_sec, 60)
        total_hour, min_part = divmod(total_min, 60)
        hour_part = total_hour
        sec_part = int(sec_rem)
        subsec = str(sec_rem - sec_part).split('.')[-1][0:4]
        x = f'{int(total_hour):02d}:{int(min_part):02d}:{sec_part:02d}.{subsec}'
        # delta = timedelta(seconds=sec)
        sys.stdout.write(str(x))
        time.sleep(0.001)
        sys.stdout.write('\r')
except KeyboardInterrupt:
    print('')
    print(timer.toc())

"""
python ~/misc/learn/stopwatch.py
"""
