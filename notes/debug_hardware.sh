
fd

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
    sudo apt-get install -y rrdtool

    rrdtool
    
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
}
