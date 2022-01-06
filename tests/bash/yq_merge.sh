    # This is where the SD card auto-mounted for me
    SYSTEM_BOOT_DPATH="/media/$USER/system-boot"
    cat "$SYSTEM_BOOT_DPATH/network-config"

    cat "$SYSTEM_BOOT_DPATH/user-data" 
    ## Ensure yq works output should be the same
    #sed '/#.*/d' "$SYSTEM_BOOT_DPATH/user-data"  | sed '/^ *$/d'
    #yq -Y . "$SYSTEM_BOOT_DPATH/user-data"

    sed '/#.*/d' "$SYSTEM_BOOT_DPATH/network-config"  | sed '/^ *$/d'
    yq -Y . "$SYSTEM_BOOT_DPATH/network-config"

    source "$HOME/local/init/utils.sh"

    TEMP_DPATH=$(mktemp -d)

    # Add the wifi section to the network-config
    codeblock "
    renderer: networkd
    wifis:
      wlan0:
        dhcp4: true
        dhcp6: true
        optional: true
        access-points:
          \"${HOME_WIFI_NAME}\":
             password: \"${HOME_WIFI_PASS}\"
    " > "$TEMP_DPATH/network-config-extra"
    # Merge the YAML files
    # https://stackoverflow.com/a/24904276/887074
    yq -Y -s '.[0] * .[1]' "$SYSTEM_BOOT_DPATH/network-config" "$TEMP_DPATH/network-config-extra" > "$TEMP_DPATH/network-config-combo"

    cat "$TEMP_DPATH/network-config-combo"

    mv "$TEMP_DPATH/network-config-combo" "$SYSTEM_BOOT_DPATH/user-data"
    chmod 611 "$SYSTEM_BOOT_DPATH/user-data"  # -rw-r--r--

    # Append this to the end of user-data
    codeblock "
    ##Reboot after cloud-init completes
    power_state:
      mode: reboot
    " > "$TEMP_DPATH/user-config-extra"
    # Merge the YAML files
    # https://stackoverflow.com/a/24904276/887074
    yq -Y -s '.[0] * .[1]' "$SYSTEM_BOOT_DPATH/user-data" "$TEMP_DPATH/user-config-extra" > "$TEMP_DPATH/user-data-combo"
    mv "$TEMP_DPATH/user-data-combo" "$SYSTEM_BOOT_DPATH/user-data"
    chmod 611 "$SYSTEM_BOOT_DPATH/user-data"  # -rw-r--r--

