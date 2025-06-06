#!/bin/bash

BACKUP_DIR="/opt/images"
DOCKER_HUB="registry.docker.io:5000"
IMAGE_LIST=$(docker images -q --format '{{.Repository}}:{{.Tag}}' | grep "${DOCKER_HUB}")

mkdir ${BACKUP_DIR}
docker images --format "{{.Repository}}:{{.Tag}} ---> {{.ID}}" > ${BACKUP_DIR}/images_list.txt
echo "start..."
for image in $IMAGE_LIST;
do
   
   BACKUP_FILE="${BACKUP_DIR}/$(echo $image | tr '/' '_' | tr ':' '-').tar"
   echo "$image is backuping to $BACKUP_FILE..."
   docker save -o $BACKUP_FILE $image 
   
   if [[ $? -eq 0 ]]; then
      echo "$BACKUP_FILE backuped successfully"
   else
      echo "$image backuped failed"
   fi

 done
 echo "finished!"


