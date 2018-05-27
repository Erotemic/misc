
list_all_users(){
    # http://www.lostsaloon.com/technology/how-to-list-all-users-in-linux/

    # all local users
    cut -d: -f1 /etc/passwd

    # all real users
    cat /etc/passwd | grep '/home' | cut -d: -f1

    # ALL users 
    getent passwd | cut -d: -f1
}

list_all_groups(){
    # all group info
    cat /etc/group

    # only groupnames
    cut -d: -f1  /etc/group
}

add_users(){
    sudo adduser username
}

make_group(){
    sudo groupadd groupname
    # Add users to the group
    sudo usermod -a -G groupname username
}

delete_a_user(){
    # Delete a user
    sudo userdel username
    sudo rm -r /home/username
}
