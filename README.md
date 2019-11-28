# Wikidata DP Portal Prototype
A prototype for the Wikidata digital preservation portal.

## Pre-requisites
  - Git or a copy of the latest source code
  - MacOS or Linux. Sorry Windows isn't currently supported.
  - Python 3. Python 2 isn't supported.
  - [Python pip](https://pip.pypa.io/en/stable/) for installing Python modules.

Using virtual environments for Python will save a lot of pain and allow you to
run Python 3 and Python 2 applications in harmony. If that sounds good then read [this primer](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

## Quick Start
The portal is a Flask web application written in Python. It's currently easy to install as long as you have a Python 3 environment. Be aware that this is currently a local development installation, it's not ready for deployment as a reliable application to a server. We're working on that. That said there's a few stages to getting going:
1. Getting the code.
2. Setting up a Python 3 virtualenv (optional but reccommended).
3. Installing the portal prototype and its dependencies.
4. Running the portal.

Let's take a look in a little more detail. We've provided some helper scripts for virtualenv setup, deployment and running which we'll also point you to.

### Getting the code
There's no helper script for this. Clone this repository and move into the project root directory:
````bash
git clone https://github.com/WikiDP/portal-proto.git
cd portal-proto
````
Alternatively download and unpack the source archive from this git repository.
````bash
wget https://github.com/WikiDP/portal-proto/archive/master.zip
unzip master.zip
rm master.zip
cd portal-proto-master
````
Once you've done this you can create the virtualenv for installation, or skip the next step if you have a Python 3 environment you're happy to use.

### Setting up a Python 3 virtualenv (optional)
We need to create a Python virtualenv in the project root folder in a `venv` subdirectory and activate it thus:
````bash
virtualenv -p python3 venv
source ./venv/bin/activate
````
There's a helper script in the root directory you can run instead:
`$ ./venv.sh`. If this has worked your terminal prompt should be adorned with a venv marker, e.g. `(venv) $`.

You only need to create the virtualenv once, although you can remove it by simply deleting the `venv` subdirectory. You'll need to activate the virtualenv `source ./venv/bin/activate` every time you start a new terminal session.

### Installing the application and dependencies
Installing the application is straightforward using `pip`:
````bash
(venv) $ source ./venv/bin/activate
(venv) $ pip install -e .
````
Where the `-e` switch tells pip to monitor the directory and recompile changes. This is useful for development but should be omitted for stable deployments.

Again there's a helper script for this: `(venv) $ ./setup.sh`.

### Running the application
The following steps need to be followed for every new terminal session.

You'll need to set up your Wikidata user name and password credentials, these can be exported as environment variables for now along with another variable that sets the flask application name:
````bash
(venv) $ export WIKIDP_BOT_USER='<username>'
(venv) $ export WIKIDP_BOT_PASSWORD='<password>'
(venv) $ export FLASK_APP='wikidp'
````
where `<username>` and `<password>` are your user name and password.

**NOTE** *these will need to be set for every new session for now*.

Finally run the  Flask application:

````bash
(venv) $ flask run
````
There's a script that you can use for this in the project root, `run.sh`. You'll need to edit it once to provide your Wikdata credentials by replacing the placeholders in the script here:
````bash
export WIKIDP_BOT_USER='<username>'
export WIKIDP_BOT_PASSWORD='<password>'
````

Point your browser to <http://127.0.0.1:5000> and you should see the prototype of the portal.

Testing the application
--------------
All Tests are currently in the _tests/_ directory. We use py.test to manage our testing interface.

### Running Tests
````bash
(venv) $ pytest
````

### Checking test coverage
We have provided a bash script to handle the coverage reporting
````bash
(venv) $ ./coverage_report.sh
````
If you would prefer a more visual web-interface for the coverage report,
this creates an _htmlcov/index.html_ file for browser viewing
````bash
(venv) $ ./coverage_report.sh visual
````

## Ansible roll out

### Local vagrant VM
`vagrant up`

### Install Ansible roles locally
```bash
ansible-galaxy install -r ansible/requirements.yml
```

#### Ansible CLI roll out to local Vagrant VM
```bash
ansible-playbook --key-file=.vagrant/machines/default/virtualbox/private_key -v --inventory ansible/vagrant vagrant.yml
```

#### First time setup for any server via SSH, needs root password for server
```bash
ansible-playbook ansible/setup.yml -i ansible/staging.yml -u root -vv -k
```
<https://unix.stackexchange.com/questions/332641/how-to-install-python-3-6>
wget <https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz>
tar xvf Python-3.6.3.tgz
cd Python-3.6.3
./configure --enable-optimizations
make -j8
sudo make altinstall
python3.6

## Troubleshooting

### Set FLASK_APP env variable
If you see something like:
```shell
Usage: flask run [OPTIONS]

Error: Could not locate Flask application. You did not provide the FLASK_APP environment variable.

For more information see http://flask.pocoo.org/docs/latest/quickstart/
```
You need to set the FLASK_APP environment variable, see Quick Start above.

This code is released under the GPLv3 license.
