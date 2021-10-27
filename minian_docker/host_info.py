import platform
import subprocess
import re

"""
WhoAmI /USER /FO LIST
'USER INFORMATION\n----------------\n\nユーザー名: matsuolab7910pc\\matsuolab7910\nSID:        S-1-5-21-400220949-3334754570-1221178460-1000'

WhoAmI /GROUP /FO LIST
'GROUP INFORMATION\n-----------------\n\nグループ名: Everyone\n種類:       よく知られたグループ\nSID:        S-1-1-0\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\ローカル アカウントと Administrators グ ループのメンバー\n種類:       よく知られたグループ\nSID:        S-1-5-114\n属性:       拒否のみに使用するグループ\n\nグ ループ名: Matsuolab7910PC\\docker-users\n種類:       エイリアス\nSID:        S-1-5-21-400220949-3334754570-1221178460-1003\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: Matsuolab7910PC\\HomeUsers\n種類:       エイリアス\nSID:        S-1-5-21-400220949-3334754570-1221178460-1001\n属性:       固定グループ, 既定で有効, 有効なグループ\n\n グループ名: BUILTIN\\Administrators\n種類:       エイリアス\nSID:        S-1-5-32-544\n属性:       拒否のみに使用するグ ループ\n\nグループ名: BUILTIN\\Performance Log Users\n種類:       エイリアス\nSID:        S-1-5-32-559\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: BUILTIN\\Users\n種類:       エイリアス\nSID:        S-1-5-32-545\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\INTERACTIVE\n種類:       よく知られたグ ループ\nSID:        S-1-5-4\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: CONSOLE LOGON\n種類:       よく知られたグループ\nSID:        S-1-2-1\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\Authenticated Users\n種類:       よく知られたグループ\nSID:        S-1-5-11\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\This Organization\n種類:       よく知られたグループ\nSID:        S-1-5-15\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\ローカル アカウント\n種類:       よく知られたグループ\nSID:        S-1-5-113\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: LOCAL\n種類:       よく知られたグループ\nSID:        S-1-2-0\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: NT AUTHORITY\\NTLM Authentication\n種類:       よく知られたグループ\nSID:        S-1-5-64-10\n属性:       固定グループ, 既定で有効, 有効なグループ\n\nグループ名: Mandatory Label\\Medium Mandatory Level\n種類:       ラベル\nSID:        S-1-16-8192\n属性:'
"""

def fetch_host_info():
    uname, uid, gname, gid = '', '', '', ''
    if platform.system() == 'Windows':
        user_command = ['WhoAmI', '/USER', '/FO', 'LIST']
        user_info    = _exec_command(user_command)

        uname, uid = _get_user_info(user_info)

        group_command = ['WhoAmI', '/GROUPS', '/FO', 'LIST']
        group_info    = _exec_command(group_command)

        gname, gid = _get_group_info(group_info)
    else:
        uname_command = ['id', '-un']
        uid_command   = ['id', '-u']
        gname_command = ['id', '-gn']
        gid_command   = ['id', '-g']

        uname = _exec_command(uname_command)
        uid   = _exec_command(uid_command)
        gname = _exec_command(gname_command)
        gid   = _exec_command(gid_command)

    return [uname, uid, gname, gid]

def _exec_command(command):
    return subprocess.run(command, capture_output=True, text=True).stdout.strip()

def _get_user_info(user_info_str):
    m = re.search('USER INFORMATION\n[-]+?\n\n[^-]+?:\s(.+?)\nSID:[\s]+?([A-Z0-9-]+)$', user_info_str)
    if m is None:
        return []

    return [m.group(1), m.group(2)]

def _get_group_info(group_info_str):
    m = re.search(':[\s]+?(.+?HomeUsers)\n.+\nSID:\s+?([A-Z0-9-]+?)\n', group_info_str)
    if m is None:
        return []

    return [m.group(1), m.group(2)]
