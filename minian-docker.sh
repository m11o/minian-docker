#!/bin/bash

DOCKER=${DOCKER:-docker}

get_mount_args() {
    args="-v $(pwd):/app -w /app"
    echo ${args[@]}
}

get_container_name() {
    echo velonica2227/minian-docker-$1
}

get_local_container_name() {
    echo minian-docker-$1
}

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

update() {
    $DOCKER pull $(get_countainer_name $1)
}

build() {
    tag=$1
    __build $(get_container_name $tag) $(get_local_container_name $tag) || exit 1
}

__build() {
    remote_name=$1
    local_name=$2

    uname=$(id -un)
    uid=$(id -u)
    gname=$(id -gn)
    gid=$(id -g)

    log "Configuring a local container for user $uname ($uid) in group $gname ($gid)"

    $DOCKER build -t ${local_name} - ${__docker_structure}

    if [ $? -ne 0 ]; then
        log Build failed.
        exit 1
    fi
    log Build succeeded
}

__docker_structure() {
    echo <<EOS
    from ${remote_name}

    run mkdir -p /home
    run mkdir -p /app
    run groupadd -g $gid $gname || groupmod -o -g $gid $gname
    run useradd -d /home -s /bin/bash -u $uid -g $gid $uname
    run chown -R $uname:$gname /home
    run chown -R $uname:$gname /app

    user $uname
EOS
}
