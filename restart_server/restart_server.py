#!/usr/bin/python

import sys

from fabric.api import local


def restart_nginx():
    local("nginx -t")
    local("/etc/init.d/nginx restart")


def restart_apache():
    local("apache2ctl -t")
    local("/etc/init.d/apache2 restart")


def restart_uwsgi(version):
    local("supervisorctl restart %s" % (version,))


if __name__ == '__main__':
    command = sys.argv[1]

    if command.startswith("uwsgi"):
        command = command.replace('.', '')
        restart_uwsgi(command)
    else:
        locals()['restart_%s' % (command,)]()
