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

change_data_dir(){
    # https://boinc.berkeley.edu/forum_thread.php?id=9633#:~:text=Move%20data%20directory.,you%20moved%20the%20data%20directory.

    # Stop the client
    sudo service boinc-client stop

    NEW_DATA_DPATH=/data/service/boinc-client
    mkdir -p "$NEW_DATA_DPATH"
    echo "$NEW_DATA_DPATH"

    # Copy to the new data dir
    sudo rsync -avrpRP /var/lib/./boinc-client /data/service/

    sudo mv /var/lib/boinc-client /var/lib/boinc-client-old
    sudo ln -s "$NEW_DATA_DPATH" /var/lib/boinc-client

    cat /etc/boinc-client/config.properties  | grep data_dir
    cat /etc/default/boinc-client | grep BOINC_DIR -C 10
    cat /usr/lib/systemd/system/boinc-client.service | grep WorkingDirectory -C 10

    # Ehhh, this is a pain, try a symlink instead
    # Change directory in the config files (Doesnt seem to do anything?)
    #sudo sed -i "s|BOINC_DIR=.*|BOINC_DIR=\"$NEW_DATA_DPATH\"|g" /etc/default/boinc-client
    #sudo_writeto /etc/boinc-client/config.properties "data_dir=$NEW_DATA_DPATH"
    # Change data dir in the service file
    #sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$NEW_DATA_DPATH|g" /usr/lib/systemd/system/boinc-client.service

    # Fix permissions
    sudo chown boinc:boinc -R "$NEW_DATA_DPATH"

    # Restart the client
    sudo service boinc-client start
    sudo service boinc-client status

    sudo systemctl daemon-reload

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
