#!/bin/bash

#set hosts
if grep "registry.docker.io" /etc/hosts; then
    echo "hosts is edited"
else 
    sudo sed -i '$ a 10.10.6.204    registry.docker.io' /etc/hosts  
fi

#downloading softwares...
sudo apt install wget -y
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

for link in "${links[@]}";
do
    sudo wget $link  -P /home/nullmax/Downloads/softwares 
    #finding all softwares...
    softwares=($(find softwares -maxdepth 3 -type f -exec echo {} \;))
    if [[ $softwares == *.sh || $softwares == *linux-ipguard.run || $softwares == *YunShu*.deb ]]; then
            continue 
    fi  
    echo "start to install $softwares"
    sudo rm -f $softwares
    echo "start to remove $softwares package"
done

