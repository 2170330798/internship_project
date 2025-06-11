# !/bin/bash 

############################################
# 1.执行完脚本后需要配置/etc/prometheus/prometheus.yml文件
############################################

# 创建文件存放目录
sudo touch /etc/systemd/system/prometheus.service
sudo mkdir /usr/local/prometheus 
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus

# 下载二进制包
wget "https://github.com/prometheus/prometheus/releases/download/v3.4.1/prometheus-3.4.1.linux-amd64.tar.gz" -O /usr/local/prometheus/prometheus-3.4.1.linux-amd64.tar.gz

# 解压和移动文件
sudo tar -xzvf /usr/local/prometheus/prometheus-3.4.1.linux-amd64.tar.gz
sudo mv /usr/local/prometheus/prometheus-3.4.1.linux-amd64/prometheus /usr/bin/prometheus
sudo mv /usr/local/prometheus/prometheus-3.4.1.linux-amd64/promtool /usr/bin/promtool
sudo mv /usr/local/prometheus/prometheus-3.4.1.linux-amd64/prometheus.yml /etc/promethues

sudo cat <<EOF> /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus Server

[Service]
User=root
ExecStart=/usr/local/bin/prometheus \
        --config.file=/etc/prometheus/prometheus.yml \
        --storage.tsdb.path=/var/lib/prometheus
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启动prometheus服务
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl restart prometheus

# 清除安装包
sudo rm -f /usr/local/prometheus/prometheus-3.4.1.linux-amd64.tar.gz
sudo rm -rf /usr/local/prometheus/prometheus-3.4.1.linux-amd64

