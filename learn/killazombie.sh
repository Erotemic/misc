# Notes on killing zombies.
__doc__="

# Find the PID of your nvidia zombies
fuser -v /dev/nvidia*

lsof -t /dev/nvidia0

https://github.com/pytorch/pytorch/issues/4293
https://stackoverflow.com/questions/4354257/can-i-stop-all-processes-using-cuda-in-linux-without-rebooting
"

# Interactive 
fuser -vki /dev/nvidia*

188770

# Zombie killer
python -c "
# Reference:
# https://github.com/Syllo/nvtop/issues/70
import ubelt as ub
import pandas as pd
import io
import rich
import rich.prompt
app_csv_text = ub.cmd('''nvidia-smi  --query-compute-apps='pid,name,gpu_uuid,used_memory' --format=csv''')['out']
gpu_csv_text = ub.cmd('''nvidia-smi  --query-gpu='index,memory.total,memory.used,memory.free,count,name,gpu_uuid,pci.bus_id,pstate' --format=csv''')['out']
app_table = pd.read_csv(io.StringIO(app_csv_text), skipinitialspace=True)
gpu_table = pd.read_csv(io.StringIO(gpu_csv_text), skipinitialspace=True)
print('')
print('App Table')
rich.print(app_table)
print('')
print('GPU Table')
rich.print(gpu_table)
# These rows might be zombies
candidate_rows = app_table[app_table['process_name'] == '[Not Found]']

if len(candidate_rows):
    print('')
    print('Candidate Zombies')
    rich.print(candidate_rows)
    if rich.prompt.Confirm.ask('Detected what might be a zombie process. Kill it?'):
        for bad_pid in candidate_rows['pid']:
            ...
        ...

    for pid in psutil.pids():
        proc = psutil.Process(pid)
        if pid == bad_pid:
            raise Exception
        for parent in proc.parents():
            if parent.pid == bad_pid:
                raise Exception
            ...

    # Need to figure out how to map the pid to the thing we really want to kill.
    import pynvml
    pynvml.nvmlInit()
    for idx in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
        uuid = pynvml.nvmlDeviceGetUUID(handle)
       
else:
    print('No zombies detected')
"
