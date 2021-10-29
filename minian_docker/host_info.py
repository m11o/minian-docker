import platform
import subprocess
import re


def fetch_host_info():
    uname, uid, gname, gid = '', '', '', ''
    if platform.system() == 'Windows':
        user_command = ['WhoAmI', '/USER', '/FO', 'LIST']
        user_info = _exec_command(user_command)

        uname, uid = _get_user_info(user_info)

        group_command = ['WhoAmI', '/GROUPS', '/FO', 'LIST']
        group_info = _exec_command(group_command)

        gname, gid = _get_group_info(group_info)
    else:
        uname_command = ['id', '-un']
        uid_command = ['id', '-u']
        gname_command = ['id', '-gn']
        gid_command = ['id', '-g']

        uname = _exec_command(uname_command)
        uid = _exec_command(uid_command)
        gname = _exec_command(gname_command)
        gid = _exec_command(gid_command)

    return [uname, uid, gname, gid]


def _exec_command(command):
    return subprocess.run(command, capture_output=True, text=True).stdout.strip()


def _get_user_info(user_info_str):
    m = re.search(r'USER INFORMATION\n[-]+?\n\n[^-]+?:\s(.+?)\nSID:[\s]+?([A-Z0-9-]+)$', user_info_str)
    if m is None:
        return []

    return [m.group(1), m.group(2)]


def _get_group_info(group_info_str):
    m = re.search(r':[\s]+?(.+?HomeUsers)\n.+\nSID:\s+?([A-Z0-9-]+?)\n', group_info_str)
    if m is None:
        return []

    return [m.group(1), m.group(2)]
