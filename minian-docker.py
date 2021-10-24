#!/usr/bin/env python3
# -*- coding utf-8 -*-

import pty
import logging
import subprocess
import textwrap
import sys
import os

from argparse import ArgumentParser

__version__ = "0.0.0.1"

ENABLE_CONTAINER_TYPES = ['bash', 'notebook']
MINIAN_NOTEBOOK_PORT = os.environ.get('MINIAN_NOTEBOOK_PORT', 8000)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]%(asctime)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S'
)

logger = logging.getLogger(__name__)

def _parse_args():
    parser = ArgumentParser('minian-docker')
    parser.add_argument(
        'container',
        type=str,
        choices=['notebook', 'bash'],
        help='The container to launch.'
    )
    return parser.parse_known_args()

def _update(container_name):
    logger.info('Update or fetching Docker image for %s' % container_name)
    command = ['docker', 'pull', container_name]
    try:
        subprocess.run(command, check=True)
    except:
        logger.error('Failed updating for docker image for %s' % container_name)
        sys.exit()

def _fetch_host_info():
    def exec_command(command):
        return subprocess.run(command, capture_output=True, text=True).stdout.strip()

    uname_command = ['id', '-un']
    uid_command   = ['id', '-u']
    gname_command = ['id', '-gn']
    gid_command   = ['id', '-g']

    uname = exec_command(uname_command)
    uid   = exec_command(uid_command)
    gname = exec_command(gname_command)
    gid   = exec_command(gid_command)

    return [uname, uid, gname, gid]

def _building_docker_commands(remote_container_name):
    host_uname, host_uid, host_gname, host_gid = _fetch_host_info()
    logger.info("Configuring a local container for user %s (%s) in group %s (%s)" % (host_uname, host_uid, host_gname, host_gid))

    commands = textwrap.dedent("""
        FROM {remote_name}

        RUN mkdir -p /home
        RUN mkdir -p /app

        RUN groupadd -g {gid} {gname} || groupmod -og {gid} {gname}
        RUN useradd -d /home -s /bin/bash -u {uid} -g {gid} {uname}
        RUN chown -R {uname}:{gname} /home
        RUN chown -R {uname}:{gname} /app

        USER {uname}
    """)
    commands = commands.format(
        remote_name=remote_container_name,
        uname=host_uname,
        uid=host_uid,
        gname=host_gname,
        gid=host_gid
    )
    return commands.strip()


def _build(remote_container_name, local_container_name):
    building_docker_command = [
        'echo', '-e', _building_docker_commands(remote_container_name)
    ]
    command = [
        'docker', 'build',
        '-t', local_container_name,
        '-'
    ]
    echo_res   = subprocess.Popen(building_docker_command, stdout=subprocess.PIPE)
    docker_res = subprocess.Popen(command, stdin=echo_res.stdout, stdout=subprocess.PIPE)
    echo_res.stdout.close()
    docker_res.communicate()

    if docker_res.returncode != 0:
        logger.error('Build failed')
        sys.exit()
    logger.info('Build succeeded.')

def _check_enable_container_type(container_type):
    if container_type not in ENABLE_CONTAINER_TYPES:
        logger.error('This container type is not available!')
        sys.exit()

    pass

def _get_container_name(container_type):
    _check_enable_container_type(container_type)
    if container_type == 'bash':
        return 'velonica2227/minian-docker-base'
    return 'velonica2227/minian-docker-%s' % container_type

def _get_local_container_name(container_type):
    _check_enable_container_type(container_type)
    if container_type == 'bash':
        return 'minian-docker-base'
    return 'minian-docker-%s' % container_type

def _run_docker(container_type):
    def exec_command(command):
        try:
            subprocess.run(command, check=True)
        except:
            logger.error('Fail to launch minian in docker.')
            sys.exit()

    container_name = _get_local_container_name(container_type)
    command = []
    if container_type == 'bash':
        command = ['docker', 'run', '-it', '--rm', container_name, 'bash']
    elif container_type == 'notebook':
        command = ['docker', 'run', '-p', '127.0.0.1:%d:8000' % MINIAN_NOTEBOOK_PORT, '-it', '--rm', container_name]

    exec_command(command)


def main():
    launch_args, docker_args = _parse_args()
    container_type = launch_args.container
    container_name = _get_container_name(container_type)
    local_container_name = _get_local_container_name(container_type)

    _update(container_name)
    _build(container_name, local_container_name)
    _run_docker(container_type)

if __name__ == "__main__":
    main()
