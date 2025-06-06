if [  -f /etc/systemd/system/yunshu-daemon.service ]; then
    
    #clean all .dep or .run packages
    #sudo rm -rf /tmp/softwares/*
    echo "OK installation finished!"
    #echo "OK installation finished!" >> /var/log/install.log
    #stop and remove service
    #sudo systemctl disable install_softwares.service --now
    #sudo systemctl stop install_softwares.service
fi