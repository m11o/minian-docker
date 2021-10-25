from setuptools import setup
from codecs import open
from os import path

import minian_docker

package_name = 'minian-docker'
root_dir = path.abspath(path.dirname(__file__))

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=package_name,
    version=minian_docker.__version__,
    description='MiniAn-docker is the package create environment of executiuon for MiniAn in Docker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/masahito1997/minian-docker',
    author='m11o',
    author_email='velonica2227@outlook.jp',
    license='GNU GPLv3',
    keywords='minian,docker,minian-docker',
    packages=[package_name],
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Topic :: Utilities'
    ],
    maintainer='m11o',
    maintainer_email='velonica2227@outlook.jp',
    entry_points={
        'console_scripts': ['minian-docker = minian_docker:main']
    },
    py_modules=['minian_docker']
)
