#!/bin/bash

# https://boinc.berkeley.edu/wiki/Boinccmd_tool

boinc_cli_demo(){
    cd etc/boinc-client && boinccmd --host localhost --passwd "" --get_state
    cd etc/boinc-client && boinccmd --host localhost --passwd "" --get_host_info

    (cd /etc/boinc-client && boinccmd --set_run_mode auto)
    (cd /etc/boinc-client && boinccmd --set_gpu_mode auto)

    (cd /etc/boinc-client && boinccmd --set_run_mode never)
    (cd /etc/boinc-client && boinccmd --set_gpu_mode never)

    boinccmd --host localhost --passwd "" --set_gpu_mode always

    # Need credentials, seems like they are empty?
    # /etc/boinc-client/gui_rpc_auth.cfg
    cat /var/lib/boinc/gui_rpc_auth.cfg

    ls /var/lib/boinc -al
    ls /var/lib/boinc-client -al
}


world_community_grid(){
    ___doc__="
    Instructions for installing worldcommunitygrid
    https://www.worldcommunitygrid.org/join.action#os-linux-debian

    TODO:
        - [ ] How do we hook contributing to WCG up to ETH or some other cyrpto as a proof-of-useful-work mechanism?
    "
    #1. In a terminal window, run the following command:
    sudo apt install boinc-client boinc-manager
    #2. Set the BOINC client to automatically start after you restart your computer:
    sudo systemctl enable boinc-client
    #3. Start the BOINC client:
    sudo systemctl start boinc-client
    #4. Allow group access to client access file:
    sudo chmod g+r /var/lib/boinc-client/gui_rpc_auth.cfg
    #5. Add your Linux user to the BOINC group to allow the BOINC Manager to communicate with the BOINC client
    sudo usermod -a -G boinc "$USER"
    #6. Allow your terminal to pick up the privileges of the new group:
    # shellcheck disable=SC2093
    exec su "$USER"
    #7. In the same terminal window, start the BOINC Manager:
    sudo boincmgr -d /var/lib/boinc-client
    
}


install_boinc()
{
    # Probably want to install a desktop
    sudo apt install ubuntu-desktop -y  # TODO: make non-interactive, might require reboot

    sudo apt install boinc-client boinc-manager -y

    sudo apt-get install boinc-client

    sudo usermod -a -G boinc "$USER"

    #sudo apt-get remove boinc-client

    # Add main computer as a host that is allowed to control this device
    printf "\n192.168.222.16\n" >> remote_hosts.cfg

    #boinc --daemon --allow_remote_gui_rpc
    boinc
    # Start boinc, then look at /var/lib/boinc/gui_rpc_auth.cfg for the password
    sudo cat /var/lib/boinc/gui_rpc_auth.cfg

    # Start the client as a service
    sudo /etc/init.d/boinc-client start
    sudo /etc/init.d/boinc-client stop

    systemctl status boinc-client.service

    # Attach boinc to WCD account
    _on_host_="
    load_secrets
    echo "export BOINC_WCG_ACCOUNT_KEY=$BOINC_WCG_ACCOUNT_KEY"
    export BOINC_WCG_ACCOUNT_KEY=...
    "

    sudo chmod 664 /etc/boinc-client/gui_rpc_auth.cfg
    #boinc --no_gui_rpc --attach_project http://www.worldcommunitygrid.org "$BOINC_WCG_ACCOUNT_KEY"
    #boinc --attach_project http://www.worldcommunitygrid.org "$BOINC_WCG_ACCOUNT_KEY"
    boinc 
    #/var/lib/boinc/gui_rpc_auth.cfg
}
