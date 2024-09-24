import pwd
import grp
import os
from utils.insert_logs import insert_logs

def privilege_descalation(confs):
    
    uid_name = confs.get("taskmaster", {}).get("uid", "user")
    gid_name = confs.get("taskmaster", {}).get("gid", "user")

    if os.geteuid() != 0:
        return

    uid = pwd.getpwnam(uid_name).pw_uid
    gid = grp.getgrnam(gid_name).gr_gid

    os.setgid(gid)
    os.setgroups([])

    os.setuid(uid)

    os.umask(0o077)
   