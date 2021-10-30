#!/usr/bin/env python3
# -*- coding utf-8 -*-

import sys

from argparse import ArgumentParser
from minian_docker.docker import Docker


def _parse_args():
    parser = ArgumentParser('minian-docker', description='It is command to launch for minian in Docker container.')
    parser.add_argument(
        'container',
        type=str,
        choices=['notebook', 'bash'],
        help='select a docker container type to launch for minian'
    )
    return parser.parse_known_args()


def main():
    args, _ = _parse_args()

    docker = Docker(args.container)
    docker.update()
    docker.build()
    docker.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(status=1)
