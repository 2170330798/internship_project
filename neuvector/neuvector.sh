# !/ bin/bash 
#####################################################
#1. kubernetes集群一建部署neuvector(k8s漏洞扫描工具)
#2. Copyright@2025.6.9
#3. Wrote By JunXiTang
#####################################################

#####################################################
#4. 在neuvector-k8s.yaml文件中找到neuvector-service-webui服务，
#   需要修改 neuvector-service-webui 的集群网络类型为NodePort
#####################################################


# 基础配置:
export NEUVECTOR_VERSION="5.3.2"
export DockerHub="registry.docker.io:5000"
export DockerHubIp="10.10.6.204"
export SourceUrl="https://registry.docker.io/neuvector/manifests/main/kubernetes/${VERSION}/neuvector-k8s.yaml"
export DestPath="/home/nullmax/tangjunxi/neuvector/neuvector-k8s.yaml"

# 创建命名空间和需要的账号:
kubectl create namespace neuvector
kubectl create sa controller -n neuvector
kubectl create sa enforcer -n neuvector
kubectl create sa basic -n neuvector
kubectl create sa updater -n neuvector
kubectl create sa scanner -n neuvector
kubectl create sa registry-adapter -n neuvector

# 提前下载neuvector所需镜像, 需要科学上网:
# 官方镜像
# docker pull neuvector/manager:${NEUVECTOR_VERSION}
# docker pull neuvector/controller:${NEUVECTOR_VERSION}
# docker pull neuvector/enforcer:${NEUVECTOR_VERSION}
# docker pull neuvector/scanner:latest
# docker pull neuvector/updater:latest

# 拉取后上传至你的私有仓库:
# 重新打标签
# docker tag neuvector/manager:${NEUVECTOR_VERSION} ${DockerHub}/neuvector/manager:${NEUVECTOR_VERSION}
# docker tag neuvector/controller:${NEUVECTOR_VERSION} ${DockerHub}/neuvector/controller:${NEUVECTOR_VERSION}
# docker tag neuvector/enforcer:${NEUVECTOR_VERSION} ${DockerHub}/neuvector/enforcer:${NEUVECTOR_VERSION}
# docker tag neuvector/scanner:latest ${DockerHub}/neuvector/scanner:latest
# docker tag neuvector/updater:latest ${DockerHub}/neuvector/updater:latest
# 上传镜像
# docker push ${DockerHub}/neuvector/manager:${NEUVECTOR_VERSION}
# docker push ${DockerHub}/neuvector/controller:${NEUVECTOR_VERSION}
# docker push ${DockerHub}/neuvector/enforcer:${NEUVECTOR_VERSION}
# docker push ${DockerHub}/neuvector/scanner:latest
# docker push ${DockerHub}/neuvector/updater:latest

# 私有镜像:
docker pull ${DockerHub}/neuvector/manager:${NEUVECTOR_VERSION}
docker pull ${DockerHub}/neuvector/controller:${NEUVECTOR_VERSION}
docker pull ${DockerHub}/neuvector/enforcer:${NEUVECTOR_VERSION}
docker pull ${DockerHub}/neuvector/scanner:latest
docker pull ${DockerHub}/neuvector/updater:latest

# 配置Host:
sed -i "$ a ${DockerHubIp}  ${DockerHub::-5}"  /etc/hosts

# 下载官方的yaml部署文件(官方访问非常慢，搭建了一个私人的):
wget ${SourceUrl} -O ${DestPath}

cat ${DestPath} | grep image: 
# 修改文件默认镜像
sed -i 's@neuvector/manager:'${VERSION}'@'${DockerHu}'/neuvector/manager:'${VERSION}'@g' ${DestPath}
sed -i 's@neuvector/controller:'${VERSION}'@'${DockerHub}'/neuvector/controller:'${VERSION}'@g' ${DestPath}
sed -i 's@neuvector/enforcer:'${VERSION}'@r'${DockerHub}'/neuvector/enforcer:'${VERSION}'@g' ${DestPath}
sed -i 's@neuvector/scanner:latest@'${DockerHub}'/neuvector/scanner:latest@g' ${DestPath}
sed -i 's@neuvector/updater:latest@'${DockerHub}'/neuvector/updater:latest@g' ${DestPath}

cat ${DestPath} | grep image: 

# 部署neuvector
kubectl apply -f ${DestPath} 
kubectl get svc -n neuvector
