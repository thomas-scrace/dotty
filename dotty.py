import os
import sys
import shlex
import glob


SYS_RC_PATH = "/etc/dottyrc"
USER_RC_PATH = "~/.dottyrc"

OPTIONS = ["srcdir", "remote"]
CONF_PATH = [SYS_RC_PATH, USER_RC_PATH] # Highest priority conf file last.


def parse_conf(path):
    parsed = {}
    if not os.path.exists(path):
        return parsed
    for line in open(path):
        tokens = shlex.split(line, posix=True, comments=True)
        if len(tokens) is 2:
            parsed[tokens[0]] = tokens[1]
    return parsed


def get_env():
    env = {}
    confs = [parse_conf(p) for p in CONF_PATH]
    for opt in OPTIONS:
        for c in confs:
            env = dict(env.items() + c.items())
    return env


def role_dir(role):
    if not os.path.isdir(role_dir):
        print "{} role does not exist.".format(role)
        sys.exit(1)
    return os.path.join(ENV["srcdir"], role)


def role_conf(role):
    conf = {}
    conf["name"] = role
    conf["dir"] = role_dir(role)
    conf["ancestors"] = []
    conf_path = os.path.join(conf["dir"], "role.conf")
    return dict(conf.items() + parse_conf(conf_path).items())


def inherit(conf):
    if "inherit" not in conf:
        return conf
    else:
        parent = conf["inherit"]
        parent_conf = role_conf(parent)
        parent_conf = inherit(conf)
        conf["ancestors"].append(parent)
        return dict(parent_conf.items() + conf.items())


def get_files(conf):
    roles = [conf["name"]] + conf["ancestors"]
    files = {}
    for r in roles:
        pattern = os.path.join(role_dir(r), "*")
        role_files = filter(glob.glob(pattern), "role.conf")
        base2abs = {os.path.basename(f): f for f in role_files}
        files = dict(base2abs.items() + files.items())
    return files


def get_ln_table(conf, files):
    ln_table = {}
    for base, abs_path in files.iteritems():
        dst = conf.get(base, "~/.{}".format(base))
        ln_table[abs_path] = dst
    return ln_table


def join(role):
    conf = role_conf(role)
    conf = inherit(conf)
    files = get_files(conf)
    ln_table = get_ln_table(conf, files)
    for target, link_name in ln_table.iteritems():
       os.symlink(target, link_name)


if __name__ == "__main__":
    ENV = get_env()
    join()
