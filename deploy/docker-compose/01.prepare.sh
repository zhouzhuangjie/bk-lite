source "./env.sh"
source "./common.sh"

log "INFO" "安装Docker..."

log "INFO" "创建Docker网络..."
docker network create $DOCKER_NETWORK

# 切换到 arm64 目录
cd ./$DIST_ARCH

# 遍历 arm64 目录下的所有子目录
for dir in */; do
    if [ -d "$dir" ]; then
        log "INFO" "Entering directory $dir"
        cd "$dir"

        # 遍历当前子目录下所有以 .tar 结尾的文件
        for file in *.tar; do
            if [ -f "$file" ]; then
                log "INFO" "Loading Docker image from $file"
                docker load -i "$file"
                if [ $? -eq 0 ]; then
                    log "INFO" "Successfully loaded Docker image from $file"
                else
                    log "ERROR" "Failed to load Docker image from $file"
                fi
            fi
        done

        # 返回上级目录
        cd ..
    fi
done