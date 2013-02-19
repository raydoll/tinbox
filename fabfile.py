# -*- coding: utf-8 -*-

from fabric.api import cd, run, settings, sudo, task, env, put
from fabric.colors import red, green
from fabric.contrib.files import exists, upload_template
from fabric.operations import prompt

env.roledefs = {
    'test_sites': ['173.255.254.234:2200', '50.116.6.38:2200'],
    'training':   ['50.116.4.76:2200']
}


@task
def create_apache_project(project, domain, py_version='2.7'):

    # Check to see if this domain already exists.. abort if it does
    if exists("/opt/webapps/{domain}".format(domain=domain)):
        print red("This project already exists.")
        return

    # Check to see if Apache is already broken and warn the user about it
    apache_broken = False
    with settings(warn_only=True):
        apache_status = sudo("apache2ctl -t")
        if not apache_status.succeeded:
            apache_broken = True
            response = prompt(red("Apache is currently BROKEN!  Are you SURE you want to continue?"), default="n")
            if response.lower() == 'n':
                return

    # Create the group for this project if it does not exist
    sudo("groupadd -f {project}".format(project=project))

    # Add the apache user to this project's group so it can read what it needs to read
    sudo("usermod -a -G {project} www-data".format(project=project))

    # Create the directory, chmod it
  #  with cd("/opt/webapps"):
   #     sudo("mkdir -p {domain}/static".format(domain=domain))

    with cd("/opt/webapps/{domain}".format(domain=domain)):
        sudo("virtualenv --distribute --no-site-packages --python=python{py_version} env".format(py_version=py_version))
        sudo("chmod -R 2770 ./")

    cxt = {
        'py_version': py_version,
        'project': project,
        'domain': domain,
        'ip_address': run("hostname -i"),}

    upload_template(
        "myvirtualdjango.py",
        "/opt/webapps/{domain}/env/myvirtualdjango.py".format(domain=domain),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=2770)

    # Upload the apache project template
    upload_template(
        "project.apache",
        "/opt/webapps/{domain}/{project}.apache".format(project=project),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=774)

    # Upload the README template
    upload_template(
        "README",
        "/opt/webapps/{domain}/README".format(domain=domain),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=770)

    # Chown everything in the directory to root:{project}
    sudo("chown -R root:{project} /opt/webapps/{domain}".format(project=project, domain=domain))

    # Fix up permissions
    sudo("chmod -R 2770 /opt/webapps/{domain}".format(domain=domain))

    # Create a sym-link from the apache config to sites-enabled
    sudo("ln -sf /opt/webapps/{domain}/{domain}.apache /etc/apache2/sites-enabled/{domain}".format(domain=domain))

    # Check apache to make sure the config we just sym-linked is valid.. if it's not, remove the link
    with settings(warn_only=True):
        apache_status = sudo("apache2ctl -t")
        if not apache_status.succeeded and not apache_broken:
            print red("Your Apache config file is BAD!  I'm going to remove the sym-link so we don't break the server.")
            sudo("rm /etc/apache2/sites-enabled/{domain}".format(domain=domain))

    # Reload apache so the config changes take effect
    sudo("/etc/init.d/apache2 reload")


@task
def create_nginx_project(project, domain, py_version='2.7'):

    # Check to see if this domain already exists.. abort if it does
    if exists("/opt/webapps/{domain}".format(domain=domain)):
        print red("This project already exists.")
        return

    # Check to see if NGINX is already broken and warn the user about it
    nginx_broken = False
    with settings(warn_only=True):
        nginx_status = sudo("nginx -t")
        if not nginx_status.succeeded:
            nginx_broken = True
            response = prompt(red("NGINX is currently BROKEN!  Are you SURE you want to continue?"), default='n')
            if response.lower() == 'n':
                return

    # Create the group for this project if it does not exist
    sudo("groupadd -f {project}".format(project=project))

    # Add the uwsgi user to this project's group so it can read what it needs to read
    sudo("usermod -a -G {project} uwsgi".format(project=project.replace(".", "")))

    # Add the nginx user to this projects group so it can read what it needs to read.
    sudo("usermod -a -G {project} www-data".format(project=project.replace(".","")))

    # Create the directory, chmod it
    with cd("/opt/webapps"):
        sudo("mkdir -p {domain}/static".format(domain=domain))

    with cd("/opt/webapps/{domain}".format(domain=domain)):
        sudo("virtualenv --distribute --no-site-packages --python=python{py_version} env".format(py_version=py_version))
        sudo("chmod -R 2770 ./")

    cxt = {
        'py_version': py_version,
        'project': project,
        'domain': domain,
        'ip_address': run("hostname -i"),
        'uwsgi_version': "django{0}".format(py_version.replace('.', ''))}

    # Upload the uwsgi config template
    upload_template(
        "myvirtualdjango.py",
        "/opt/webapps/{domain}/env/myvirtualdjango.py".format(domain=domain),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=2770)

    # Upload the nginx project template
    upload_template(
        "project-nginx.conf",
        "/opt/webapps/{domain}/{domain}.nginx".format(domain=domain),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=774)

    # Upload the README template
    upload_template(
        "README",
        "/opt/webapps/{domain}/README".format(domain=domain),
        context=cxt,
        use_jinja=True,
        template_dir="templates",
        use_sudo=True,
        mode=770)

    # Chown everything in the directory to root:{project}
    sudo("chown -R root:{project} /opt/webapps/{domain}".format(project=project, domain=domain))

    # Fix up permissions
    sudo("chmod -R 2770 /opt/webapps/{domain}".format(domain=domain))

    # Create a sym-link from the nginx config to sites-enabled
    sudo("ln -sf /opt/webapps/{domain}/{domain}.nginx /etc/nginx/sites-enabled/{domain}".format(domain=domain))

    # Check nginx to make sure the config we just sym-linked is valid.. if it's not, remove the link
    with settings(warn_only=True):
        nginx_status = sudo("nginx -t")
        if not nginx_status.succeeded and not nginx_broken:
            print red("Your NGINX config file is BAD!  I'm going to remove the sym-link so we don't break the server.")
            sudo("rm /etc/nginx/sites-enabled/{domain}".format(domain=domain))

    # Reload nginx so the config changes take effect
    sudo("/etc/init.d/nginx reload")


@task
def deploy_scripts():
    sudo("pip install fabric==1.4.1")

    put("restart_server/restart_server.c", "/var/tmp")
    put("restart_server/restart_server.py", "/usr/local/bin", use_sudo=True)

    with cd("/var/tmp"):
        sudo("gcc -o restart_server restart_server.c")
        sudo("mv ./restart_server /usr/local/bin/")

    sudo("groupadd -f dev")

    sudo("chown root:root /usr/local/bin/restart_server.py")
    sudo("chown root:dev  /usr/local/bin/restart_server")

    sudo("chmod 0700 /usr/local/bin/restart_server.py")
    sudo("chmod 4750 /usr/local/bin/restart_server")
