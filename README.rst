How to get this up and running:

1. Create a virtualenvironment and source into it::

    virtualenv --distribute --no-site-packages --python=python2.7 tinbox-env
    cd tinbox-env
    source bin/activate

2. Clone the git repo into the virtualenv::

    git clone git@github.com:ryanshow/tinbox.git tinbox

3. Install the requirements::

    pip install -r tinbox/requirements.txt

4. Run tinbox!::

   cd tinbox
   fab -u <user> -H <server_name> create_nginx_project:project=foo,domain=foo.example.com

Have Fun!
