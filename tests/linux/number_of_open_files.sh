__doc__="
References:
    https://www.netadmintools.com/art295.html#wbounce-modal
    https://stackoverflow.com/questions/48250053/pytorchs-dataloader-too-many-open-files-error-when-no-files-should-be-open

"

# Maximum number of file descriptors
cat /proc/sys/fs/file-max 


# how many file descriptors are being used
# Ouputs 3 columsn
# (1) maximum open file descriptors
# (2) total free allocated file descriptors
# (3) total allocated file descriptors (the number of file descriptors allocated since boot)
cat /proc/sys/fs/file-nr


# Number of open files
lsof | wc -l


PROC_ID=$(ps -a | awk '{print $1}' | tail -n 10 | head -n 1)
echo "PROC_ID = $PROC_ID"


ipython_proc_list_file_usage(){
    PROC_ID_LIST=($(ps -a | grep ipython | awk '{print $1}' ))
    for PROC_ID in "${PROC_ID_LIST[@]}"; do
        NUM_OPEN_FILES=$(lsof -p $PROC_ID | wc -l)
        echo "PROC_ID=$PROC_ID, NUM_OPEN_FILES=$NUM_OPEN_FILES"
    done
}
export -f ipython_proc_list_file_usage

watch -x bash -c '
    PROC_ID_LIST=($(ps -a | grep python | awk '"'"'{print $1}'"'"' ))
    for PROC_ID in "${PROC_ID_LIST[@]}"; do
        NUM_OPEN_FILES=$(lsof -p $PROC_ID | wc -l)
        echo "PROC_ID=$PROC_ID, NUM_OPEN_FILES=$NUM_OPEN_FILES"
    done
'

PROC_ID=$(ps -a | grep ipython | awk '{print $1}' | head -n 1)
echo "PROC_ID = $PROC_ID"

lsof -p $PROC_ID


#PROC_ID=$(ps -a | awk '{print $1}' | tail -n 10 | head -n 1)
lsof $PROC_ID
#echo "PROC_ID = $PROC_ID"
#PROC_ID=2359030
#PROC_ID=2359030
ls -l /proc/$PROC_ID/fd/
cat /proc/$PROC_ID/limits


prlimit --nofile=8192
ulimit -n 4096
