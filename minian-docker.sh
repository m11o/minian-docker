#!/bin/bash

DOCKER=${DOCKER:-docker}
MINIAN_NOTEBOOK_PORT=${MINIAN_NOTEBOOK_PORT:-8000}

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
  log "Fetching Docker image for $(get_container_name $1) ..."
  $DOCKER pull $(get_container_name $1)
}

build() {
  tag=$1
  log "Build Docker container for $(get_local_container_name $tag) ..."
  __build $(get_container_name $tag) $(get_local_container_name $tag) || exit 1
}

__build() {
  local_name=$2
  echo $(__docker_structure $1)
  $DOCKER build -t ${local_name} - $(__docker_structure $1)

  if [ $? -ne 0 ]; then
      log Build failed.
      exit 1
  fi
  log Build succeeded
}

__docker_structure() {
  remote_name=$1

  uname=$(id -un)
  uid=$(id -u)
  gname=$(id -gn)
  gid=$(id -g)

  log "Configuring a local container for user $uname ($uid) in group $gname ($gid)"

  STRUCTURE=`cat <<- EOS
  from ${remote_name}

  run mkdir -p /home
  run mkdir -p /app
  run groupadd -g $gid $gname || groupmod -o -g $gid $gname
  run useradd -d /home -s /bin/bash -u $uid -g $gid $uname
  run chown -R $uname:$gname /home
  run chown -R $uname:$gname /app

  user $uname
EOS
`

  echo $STRUCTURE
}

bash() {
  extra_args="$@"
  update base || exit 1
  build base || exit 1
  args="$(get_mount_args) ${extra_arga}"

  $DOCKER run -it --rm $args $(get_local_container_name base) bash
}

notebook() {
  extra_arga="$@"
  update notebook || exit 1
  build notebook || exit 1
  args="$(get_mount_args) ${extra_args}"

  $DOCKER run -p 127.0.0.1:${MINIAN_NOTEBOOK_PORT}:8000 -it --rm ${args} $(get_local_container_name notebook) || log "Failed to launch the notebook server."
}

subcommand=${1:-notebook}
shift 1
case "${subcommand}" in
  bash) bash "$@" ;;
  notebook) notebook "$@" ;;
  *)
    echo "Usage"
    echo "$0 [bash|notebook|help]"
    ;;
esac
