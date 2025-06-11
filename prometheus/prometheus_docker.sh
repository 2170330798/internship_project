# !/bin/bash
############################
# run prometheus with docker
############################

# 配置prometheus
sudo mkdir /etc/promethus
sudo touch /etc/prometheus/prometheus.yml
sudo cat <<EOF> /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s      # 默认抓取间隔
  evaluation_interval: 15s  # 规则评估间隔

# 告警管理器配置（需提前部署 Alertmanager）
#alerting:
#  alertmanagers:
#    - static_configs:
#        - targets: ['alertmanager:9093']

# 规则文件路径（支持通配符）
# rule_files:
#   - '/etc/prometheus/rules/recording_rules.yml'
#   - '/etc/prometheus/rules/alerting_rules.yml'

# 监控目标配置
scrape_configs:
  # 监控 Prometheus 自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['10.10.6.204:9090']

  # 监控主机资源（需运行 node_exporter）
  - job_name: 'node'
    static_configs:
      - targets: ['10.10.8.107:9100', '10.10.8.108:9100']
  


  # 监控 Docker
  - job_name: 'docker-engine'
    static_configs:
      - targets: ['10.10.6.204:9323']
  # 监控 Docker 容器
  - job_name: 'docker-cadvisor'
    static_configs:
      - targets: ['10.10.6.204:8083']
EOF

# 运行prometheus镜像
sudo docker pull prom/prometheus
sudo docker run -d \
    --restart always \
    --name prometheus \
    -p 9090:9090 \
    -v /etc/prometheus/prometheus.yml:/etc/prometheus
    prom/prometheus

# 运行grafana镜像
sudo docker pull grafana/grafana
sudo docker run -d \
  --restart always \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana


