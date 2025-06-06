#! /bin/bash

ipguard_path="/opt/softwares/linux-ipguard.run"
yunshu_path="/opt/softwares/YunShu_2.3.7.171_amd64.deb"

if [ -f /etc/systemd/system/yunshu-daemon.service ] &&  [ -f /etc/systemd/system/LAgentUser_PreLogin.service ]; then
    
    #clean all .dep or .run packages
    sudo rm -rf /opt/softwares/*
    echo "OK installation finished!"
    sudo echo "installation finished" >> /var/log/install.log
    sudo echo "install_softwares.service removed" >> /var/log/install.log
    #stop and remove service
    sudo systemctl disable install_softwares.service --now
    sudo systemctl stop install_softwares.service
   
else 
    #linux-ipguard
    if [ -f /etc/systemd/system/LAgentUser_PreLogin.service ]; then
        #yunshu
        printf "start to install $yunshu_path...\n"
        sudo echo "start to install $yunshu_path..." >> /var/log/install.log
        sudo dpkg -i $yunshu_path
    else
        printf "start to install $ipguard_path...\n"
        sudo echo "start to install $ipguard_path..." >> /var/log/install.log
        sudo rm -rf /opt/IPG-Linux/* --force
        sudo bash $ipguard_path
        if [ -f /etc/systemd/system/LAgentUser_PreLogin.service ]; then
            sudo echo "reboot, now..." >> /var/log/install.log
            sudo reboot
        fi
    fi
fi


