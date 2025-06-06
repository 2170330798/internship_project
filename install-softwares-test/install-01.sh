#!/bin/bash

#update apt source
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
sudo touch /etc/apt/sources.list
sudo cat <<EOF> /etc/apt/sources.list
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-backports main restricted universe multiverse
deb http://mirrors.huaweicloud.com/repository/ubuntu/ focal-security main restricted universe multiverse
EOF
sudo apt update

#set hosts
if grep "registry.docker.io" /etc/hosts; then
    printf "hosts is edited\n"
else 
    sudo sed -i '$ a 10.10.6.204    registry.docker.io' /etc/hosts  
fi
#downloading softwares...
links=("http://registry.docker.io/downloads/feishu/v6.9.20/Feishu-linux_x64-6.9.20.deb"
        "http://registry.docker.io/downloads/google/google-chrome-stable_current_amd64.deb"
        "http://registry.docker.io/downloads/scripts/v0.1/install-02.sh"
        "http://registry.docker.io/downloads/sogoupinyin/v2.4.0/sogoupinyin_2.4.0.3469_amd64.deb"
        "http://registry.docker.io/downloads/todest/v4.7.2.0/todesk-v4.7.2.0-amd64.deb"
        "http://registry.docker.io/downloads/vscode/v1.86.0/code_1.86.0-1706698139_amd64.deb"
        "http://registry.docker.io/downloads/wps/wps-office_11.1.0.11723.XA_amd64.deb"
        "http://registry.docker.io/downloads/yunshu/v2.3.7-171/YunShu_2.3.7.171_amd64.deb"
        "http://registry.docker.io/downloads/linux-ipguard/v4.85.408.0/linux-ipguard.run"
        )
sudo apt install wget -y
for link in "${links[@]}";
do
        sudo wget $link  -P /home/nullmax/Downloads/softwares  
        #finding all softwares...
        softwares=($(find softwares -maxdepth 3 -type f -exec echo {} \;))
        #installing all softwares...
        if [[ $softwares == *.sh || $softwares == *linux-ipguard.run || $softwares == *YunShu*.deb ]]; then
           continue 
        fi  
        printf "start to install $softwares\n"
        if [[  $softwares == *.run ]]; then
            sudo bash $softwares
        elif [[  $softwares == *.deb  ]]; then
            if [[ $softwares == *sogoupinyin* ]]; then
                   sudo dpkg -i $softwares
                   sudo apt install -f -y
            fi
            sudo dpkg -i $softwares
        else
            printf "Not a type of *.deb or *.run files!\n"
        fi
        printf "start to remove $softwares packages\n\n"
        sudo rm -f $softwares
done

#ensure normal installation of sogoupinyin
sudo apt install -f -y

#set start automatically...
sudo chmod +x /home/nullmax/Downloads/softwares/install-02.sh
sudo touch /etc/systemd/system/install_softwares.service

sudo cat <<EOF> /etc/systemd/system/install_softwares.service
[Unit]
Description="Install Softwares"

[Service]
ExecStart=/home/nullmax/Downloads/softwares/install-02.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable install_softwares.service
sudo systemctl start install_softwares.service
sudo systemctl status install_softwares.service

#enable script...
sudo bash /home/nullmax/Downloads/softwares/install-02.sh