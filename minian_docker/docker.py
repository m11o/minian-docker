import logging
import subprocess
import textwrap
import sys
import os
import re

from motd import MOTD
from host_info import fetch_host_info
from agent import is_windows, is_linux, is_macos

ENABLE_CONTAINER_TYPES = ['bash', 'notebook', 'gui']
MINIAN_NOTEBOOK_PORT = os.environ.get('MINIAN_NOTEBOOK_PORT', 8000)
DOCKER_OWNER_NAME = 'velonica2227'


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
        except Exception as e:
            self.logger.error(e)
            self.logger.error('Failed updating for docker image for %s' % self.image_name)
            sys.exit()

    def build(self):
        if is_windows():
            return  # do nothing

        building_docker_command = [
            'echo', self._building_docker_commands()
        ]
        command = [
            'docker', 'build',
            '-t', self.container_name,
            '-'
        ]
        echo_res = subprocess.Popen(building_docker_command, stdout=subprocess.PIPE)
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
            except Exception as e:
                self.logger.error(e)
                self.logger.error('Fail to launch minian in docker.')
                sys.exit()

        docker_command = ['docker', 'run', '-it', '--rm']
        docker_command.extend(self._docker_mount_args())
        docker_command.extend(self._docker_x11_args())
        docker_exec = None
        docker_option = []
        if self.container_type == 'bash':
            docker_exec = 'bash'
        elif self.container_type == 'notebook':
            docker_option = ['-p', '127.0.0.1:%d:8000' % MINIAN_NOTEBOOK_PORT]
        elif self.container_type == 'gui':
            docker_exec = ['python', 'minian_docker/gui/sample.py']

        docker_command.extend(docker_option)
        docker_command.append(self.image_name if is_windows() else self.container_name)

        if docker_exec is not None:
            if type(docker_exec) is list:
                docker_command.extend(docker_exec)
            else:
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
        host_uname, host_uid, host_gname, host_gid = fetch_host_info()
        self.logger.info(
            "Configuring a local container for user %s (%s) in group %s (%s)" % (
                host_uname,
                host_uid,
                host_gname,
                host_gid
            )
        )

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
        command = 'chdir' if is_windows() else 'pwd'
        current_directory = subprocess.run([command], capture_output=True, text=True, shell=True).stdout.strip()
        self.logger.info('Mounted current Directory: %s' % current_directory)

        return ['-v', '%s:/app' % current_directory, '-w', '/app']

    def _docker_x11_args(self):
        if is_windows():
            self.logger.info('not working')
            return []

        if is_linux():
            display_env = 'DISPLAY=unix%s' % os.environ['DISPLAY']
            xauthority_env = '%s:/home/developer/.Xauthority' % os.environ['XAUTHORITY']
            return [
                '-e', display_env,
                '-v', '/tmp/.X11-unix:/tmp/.X11-unix',
                '-v', xauthority_env
            ]
        elif is_macos():
            self.logger.info('using MacOS')

            ifconfig_command = ['ifconfig', 'en0']
            grep_command = ['grep', 'inet']
            awk_command = ['awk', "'$1==\"inet\" {print $2}'"]

            ifconfig_res = subprocess.Popen(ifconfig_command, stdout=subprocess.PIPE)
            grep_res = subprocess.Popen(grep_command, stdin=ifconfig_res.stdout, stdout=subprocess.PIPE)
            awk_res = subprocess.Popen(awk_command, stdin=grep_res.stdout, stdout=subprocess.PIPE)

            grep_res.stdout.close()
            ifconfig_res.stdout.close()

            awk_res.communicate()

            ip = awk_res.stdout
            display_env = os.environ['DISPLAY']
            display_matcher = re.search(r'^.*?(:[0-9])$', display_env)
            display_id = display_matcher.group(1)
            return ['-e', 'DISPLAY=%s%s' % (ip, display_id)]
        else:
            self.logger.error('Unknown OS')
            sys.exit()
