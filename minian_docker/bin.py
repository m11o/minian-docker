#!/usr/bin/env python3
# -*- coding utf-8 -*-

from argparse import ArgumentParser
from docker import Docker

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
