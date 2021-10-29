import platform

WINDOWS_SYSTEM_NAME = 'Windows'
MACOS_SYSTEM_NAME = 'Darwin'
LINUX_SYSTEM_NAME = 'Linux'


def is_windows():
    return platform.system() == WINDOWS_SYSTEM_NAME


def is_macos():
    return platform.system() == MACOS_SYSTEM_NAME


def is_linux():
    return platform.system() == LINUX_SYSTEM_NAME
