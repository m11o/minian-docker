#!/usr/bin/env python3
# -*- coding utf-8 -*-

import logging
import subprocess
import textwrap
import sys
import os

from argparse import ArgumentParser

__version__ = "0.0.0.4"

ENABLE_CONTAINER_TYPES = ['bash', 'notebook']
MINIAN_NOTEBOOK_PORT = os.environ.get('MINIAN_NOTEBOOK_PORT', 8000)
DOCKER_OWNER_NAME = 'velonica2227'
MOTD = """
          ____()()
         /      @@
   `~~~~~\_;m__m._>o
 _____  _____  _____  _____  _____  _____       ____   _____  _____  _____  _____  _____
|     ||     ||   | ||     ||  _  ||   | | ___ |    \ |     ||     ||  |  ||   __|| __  |
| | | ||-   -|| | | ||-   -||     || | | ||___||  |  ||  |  ||   --||    -||   __||    -|
|_|_|_||_____||_|___||_____||__|__||_|___|     |____/ |_____||_____||__|__||_____||__|__|

Welcome to minian-docker

"""

class Docker:
    def __init__(self, container_type):
        self.logger = self._build_logger()

        self.container_type = container_type
        self.image_name = self._image_name()
        self.container_name = self._container_name()

        self._check_enable_container_type()

    def update(self):
        self.logger.info('Update or fetching Docker image for %s' % self.image_name)
        command = ['docker', 'pull', self.image_name]
        try:
            subprocess.run(command, check=True)
        except:
            self.logger.error('Failed updating for docker image for %s' % self.image_name)
            sys.exit()

    def build(self):
        building_docker_command = [
            'echo', self._building_docker_commands()
        ]
        command = [
            'docker', 'build',
            '-t', self.container_name,
            '-'
        ]
        echo_res   = subprocess.Popen(building_docker_command, stdout=subprocess.PIPE)
        docker_res = subprocess.Popen(command, stdin=echo_res.stdout, stdout=subprocess.PIPE)
        echo_res.stdout.close()
        docker_res.communicate()

        if docker_res.returncode != 0:
            self.logger.error('Build failed')
            sys.exit()
        self.logger.info('Build succeeded.')

    def run(self):
        def exec_command(command):
            try:
                subprocess.run(command, check=True)
            except:
                self.logger.error('Fail to launch minian in docker.')
                sys.exit()

        docker_command = ['docker', 'run', '-it', '--rm']
        docker_command.extend(self._docker_mount_args())
        docker_exec = None
        docker_option = []
        if self.container_type == 'bash':
            docker_exec = 'bash'
        elif self.container_type == 'notebook':
            docker_option = ['-p', '127.0.0.1:%d:8000' % MINIAN_NOTEBOOK_PORT]

        docker_command.extend(docker_option)
        docker_command.append(self.container_name)
        if docker_exec is not None:
            docker_command.append(docker_exec)

        self.logger.info(' '.join(docker_command))
        print(MOTD)
        exec_command(docker_command)

    def _image_name(self):
        return '%s/%s' % (DOCKER_OWNER_NAME, self._container_name())

    def _container_name(self):
        if self.container_type == 'bash':
            return 'minian-docker-base'
        return 'minian-docker-%s' % self.container_type

    def _build_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s]%(asctime)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S'
        )

        return logging.getLogger(__name__)

    def _building_docker_commands(self):
        host_uname, host_uid, host_gname, host_gid = self._fetch_host_info()
        self.logger.info("Configuring a local container for user %s (%s) in group %s (%s)" % (host_uname, host_uid, host_gname, host_gid))

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
            remote_name=self.image_name,
            uname=host_uname,
            uid=host_uid,
            gname=host_gname,
            gid=host_gid
        )
        return commands.strip()

    def _check_enable_container_type(self):
        if self.container_type not in ENABLE_CONTAINER_TYPES:
            self.logger.error('The container is not available!')
            sys.exit()

    def _docker_mount_args(self):
        current_directory = subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()
        self.logger.info('Mounted current Directory: %s' % current_directory)

        return ['-v', '%s:/app' % current_directory, '-w', '/app']

    @staticmethod
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



def _parse_args():
    parser = ArgumentParser('minian-docker')
    parser.add_argument(
        'container',
        type=str,
        choices=['notebook', 'bash'],
        help='The container to launch.'
    )
    return parser.parse_known_args()

def main():
    args, _ = _parse_args()

    docker = Docker(args.container)
    docker.update()
    docker.build()
    docker.run()


if __name__ == "__main__":
    main()
