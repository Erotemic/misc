__doc__="
Notes about handling system services

There are two service manager interfaces systemctl and service.

* systemctl is a low level system

* service is a wrapper that wraps systemctl and older protocols: init.d and initctl


References:
    https://stackoverflow.com/questions/43537851/difference-between-systemctl-and-service-command
    https://serverfault.com/questions/867322/what-is-the-difference-between-service-and-systemctl
"


devcheck_service(){
    sudo service --status-all | grep git

}

devcheck_systemctl(){
    sudo systemctl list-units --type=service

    SERVICE_NAME=gitlab-runner.service
    sudo systemctl status $SERVICE_NAME
    sudo systemctl stop $SERVICE_NAME

    sudo systemctl list-units --type=service 
    sudo systemctl status apport-autoreport.service
    sudo systemctl restart apport-autoreport.service
    sudo systemctl stop apport-autoreport.service
    sudo systemctl start apport-autoreport.service
}
