#!/bin/bash

BACKUP_DIR="/opt/images"
DOCKER_HUB="registry.docker.io:5000"
IMAGE_LIST=$(docker images -q --format '{{.Repository}}:{{.Tag}}' | grep "${DOCKER_HUB}")

mkdir ${BACKUP_DIR}
docker images --format "{{.Repository}}:{{.Tag}} ---> {{.ID}}" > ${BACKUP_DIR}/images_list.txt
echo "start..."
echo $IMAGE_LIST
echo "finished!"


#manifest:
#search original images
grep image: /etc/calico/calico.yaml 
 
 #拉镜像
sudo docker pull docker.io/calico/cni:v3.29.1
sudo docker pull docker.io/calico/node:v3.29.1
sudo docker pull docker.io/calico/kube-controllers:v3.29.1
#打标上传镜像
sudo docker tag docker.io/calico/cni:v3.29.1   registry.docker.io:5000/cni:v3.29.1  
sudo docker tag docker.io/calico/node:v3.29.1  registry.docker.io:5000/node:v3.29.1  
sudo docker tag docker.io/calico/kube-controllers:v3.29.1  registry.docker.io:5000/kube-controllers:v3.29.1

sudo docker push registry.docker.io:5000/cni:v3.29.1  
sudo docker push registry.docker.io:5000/node:v3.29.1  
sudo docker push registry.docker.io:5000/kube-controllers:v3.29.1

