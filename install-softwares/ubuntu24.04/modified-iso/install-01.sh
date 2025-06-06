#!/bin/bash

tmp="/opt/softwares"
#lock kernel
kernel=$(uname -r)
sudo apt-mark hold ${kernel::-8}
sudo touch /etc/apt/preferences.d/linux-kernel
sudo cat <<EOF> /etc/apt/preferences.d/linux-kernel
Package: linux-image-*
Pin: version *
Pin-Priority: -1

Package: linux-headers-*
Pin: version *
Pin-Priority: -1
EOF

sudo apt update
#update apt source
sudo touch /var/log/install.log
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
sudo touch /etc/apt/sources.list
sudo cat <<EOF> /etc/apt/sources.list
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-backports main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-security main restricted universe multiverse
EOF
sudo apt update
sudo echo "update apt sources" >> /var/log/install.log
#set hosts
if grep "registry.docker.io" /etc/hosts; then
    printf "hosts is edited\n"
else 
    sudo sed -i '$ a 10.10.6.204    registry.docker.io' /etc/hosts  
fi
sudo echo "update hosts" >> /var/log/install.log

#downloading softwares...
links=( "http://registry.docker.io/downloads/yunshu/v2.3.7-171/YunShu_2.3.7.171_amd64.deb"
        ""http://registry.docker.io/downloads/install-softwares/ubuntu20.04/original-iso/scripts/install-02.sh""
        "http://registry.docker.io/downloads/linux-ipguard/v4.85.408.0/linux-ipguard.run"
        )

sudo apt install -y wget
for link in "${links[@]}"; 
do
    sudo wget sudo wget $link  -P $tmp  
done

#set start automatically...
sudo chmod +x $tmp/install-02.sh
sudo touch /etc/systemd/system/install_softwares.service
sudo echo "make a install_softwares.service file" >> /var/log/install.log
sudo cat <<EOF> /etc/systemd/system/install_softwares.service
[Unit]
Description="Install Softwares"

[Service]
ExecStart=$tmp/install-02.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable install_softwares.service
sudo systemctl start install_softwares.service
sudo systemctl status install_softwares.service
sudo echo " install_softwares.service start" >> /var/log/install.log

#enable script...
sudo bash $tmp/install-02.sh