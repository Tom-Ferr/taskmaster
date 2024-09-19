import pwd
import grp
import os
def privilege_descalation(uid_name='user', gid_name='user'):

    if os.geteuid() != 0:
        return

    uid = pwd.getpwnam(uid_name).pw_uid
    gid = grp.getgrnam(gid_name).gr_gid

    os.setgid(gid)
    os.setgroups([])

    os.setuid(uid)

    os.umask(0o077)