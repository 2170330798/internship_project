#!/bin/bash

BACKUP_DIR="/opt/images"
IMAGES_TAR=$(find ${BACKUP_DIR} -maxdepth 1 -type f ! -name "*.txt" -exec echo {} \;)
echo "start..."
for tar in $IMAGES_TAR;
do
   echo "$tar is restoring..."
   docker load -i $(echo $image | tr '_' '/' | tr '-' ':')
   if [[ $? -eq 0 ]]; then
       echo "$BACKUP_FILE restroed successfully"
   else
       echo "$image_id restored failed"
   fi

 done
 echo "finished!"

