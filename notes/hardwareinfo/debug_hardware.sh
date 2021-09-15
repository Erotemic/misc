__doc__="

Also:
    https://forums.developer.nvidia.com/t/msi-3090-gpu-causes-a-full-system-crash-when-under-any-sort-of-load-ubuntu-18-04lts/175117
    https://forums.evga.com/3090-FTW-5950X-computer-turning-off-m3237602.aspx

My Question:
    https://serverfault.com/questions/1074946/debugging-unexpected-system-shutdown

"

debug_sudden_crash(){
    __doc__="
    References: 
        https://unix.stackexchange.com/questions/502226/how-do-you-find-out-if-a-linux-machine-overheated-before-the-previous-boot-and-w
    "
    journalctl -g 'temperature|critical'
    journalctl -g 'temperature|critical' -b -2
    grep -i error /var/log/syslog

    cat /var/log/syslog
    cat /var/log/kern.log

    #/var/log/debug
    #/var/log/syslog # (will be pretty full and may be harder to browse)
    cat /var/log/user.log
    cat /var/log/kern.log

    last reboot | less
    last -x | head | tac

}

hdd_smart_info(){
    sudo smartctl --all /dev/sda 
    sudo smartctl --all /dev/sdb
    sudo smartctl --all /dev/sdc 
    sudo smartctl --all /dev/sdd
    
}

setup_temperature_logging(){
    # https://itectec.com/ubuntu/ubuntu-how-to-monitor-log-server-hardware-temperatures-load/
    # https://askubuntu.com/questions/15832/how-do-i-get-the-cpu-temperature

    
    sudo apt install lm-sensors hddtemp

    sudo sensors-detect
    #To load everything that is needed, add this to /etc/modules:
    ##----cut here----
    ## Chip drivers
    #coretemp
    #nct6775
    ##----cut here----
    

    sudo apt-get install psensor
    sudo hddtemp /dev/sda /dev/sdb /dev/sdc /dev/sdd

    # https://oss.oetiker.ch/rrdtool/
    # https://github.com/oetiker/rrdtool-1.x
    sudo apt-get install -y rrdtool

    rrdtool

    # https://github.com/torfsen/python-systemd-tutorial
    # https://www.google.com/search?q=write+linux+service+in+python&oq=write+linux+service+in+python&aqs=chrome..69i57j35i39j0j0i22i30l7.3586j0j7&sourceid=chrome&ie=UTF-8
    
    #https://stackoverflow.com/questions/473620/how-do-you-create-a-daemon-in-python

   https://www.robustperception.io/temperature-and-hardware-monitoring-metrics-from-the-node-exporter 

    # simple log script
    while true; do
        printf "\n--$( date '+%H:%M:%S' )\n$( sensors -j)\n" >> sensor.log
        sleep 2; 
    done
}


memory_check(){
    # https://linuxhint.com/run_memtest_ubuntu/
    # https://linuxhint.com/check-ram-ubuntu/
    sudo apt install memtester

    sudo dmidecode --type memory

    sudo memtester 100M 2
    sudo memtester 1024 5
    sudo memtester 8000MB 5

    # Need to reboot to grub to use this
    sudo apt install memtest86
}


zfs_issue(){
 # https://github.com/openzfs/zfs/issues/10697
 # https://github.com/openzfs/zfs/issues/3990
 echo
}

debug_crash(){
    # https://unix.stackexchange.com/questions/9819/how-to-find-out-from-the-logs-what-caused-system-shutdown
    echo
}


setup_node_exporter(){
    # https://github.com/prometheus/node_exporter/releases/
    mkdir -p $HOME/tmp/setup-node-exporter
    cd $HOME/tmp/setup-node-exporter
    # https://www.reddit.com/r/linuxquestions/comments/oht8w7/best_practice_for_continuously_monitor_and_log/

    #wget https://github.com/prometheus/node_exporter/releases/download/v1.1.2/sha256sums.txt
    #cat sha256sums.txt

    EXPECTED_SHA256="8c1f6a317457a658e0ae68ad710f6b4098db2cad10204649b51e3c043aa3e70d"
    ARCHIVE_FNAME="node_exporter-1.1.2.linux-amd64.tar.gz"
    EXTRACTED_DPATH="${ARCHIVE_FNAME%.tar.gz}"
    wget https://github.com/prometheus/node_exporter/releases/download/v1.1.2/$ARCHIVE_FNAME
    echo "$EXPECTED_SHA256 $ARCHIVE_FNAME" | sha256sum --check
    if [[ "$?" != "0" ]]; then
        exit 1
    fi
    tar xvf $ARCHIVE_FNAME
    ./$EXTRACTED_DPATH/node_exporter


    cd $HOME/tmp/setup-node-exporter
    EXPECTED_SHA256="91dd91e13f30fe520e01175ca1027dd09a458d4421a584ba557ba88b38803f27"
    ARCHIVE_FNAME="prometheus-2.28.1.linux-amd64.tar.gz"
    wget https://github.com/prometheus/prometheus/releases/download/v2.28.1/$ARCHIVE_FNAME
    GOT_SHA256=$(sha256sum $ARCHIVE_FNAME)
    echo "GOT_SHA256 = $GOT_SHA256"
    echo "$EXPECTED_SHA256 $ARCHIVE_FNAME" | sha256sum --check
    if [[ "$?" != "0" ]]; then
        exit 1
    fi
    tar xvf $ARCHIVE_FNAME
    EXTRACTED_DPATH="${ARCHIVE_FNAME%.tar.gz}"

    cat $EXTRACTED_DPATH/prometheus.yml

    $EXTRACTED_DPATH/prometheus --config.file=$EXTRACTED_DPATH/prometheus.yml

    curl http://localhost:9100/metrics

    sed -i 's/localhost:9090/localhost:9100/g' ./prometheus-2.28.1.linux-amd64/prometheus.yml
    cat ./prometheus-2.28.1.linux-amd64/prometheus.yml

    echo "$(codeblock "
    #
      - job_name: node
        static_configs:
        - targets: ['localhost:9100']
      ")" >> ./prometheus-2.28.1.linux-amd64/prometheus.yml
    ./prometheus-2.28.1.linux-amd64/prometheus --config.file=./prometheus-2.28.1.linux-amd64/prometheus.yml


    docker run -d \
      --net="host" \
      --pid="host" \
      -v "/:/host:ro,rslave" \
      quay.io/prometheus/node-exporter:latest \
      --path.rootfs=/host
    
        
}
