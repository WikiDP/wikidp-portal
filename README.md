Wikidatata DP Portal Prototype
==============================

Pre-requisites
--------------
 - MacOS or Linux (won't work as is on Windows)
 - python

Quick Start
-----------
All instructions currently
Clone this repository and move into the project root directory:

    git clone https://github.com/WikiDP/portal-proto.git
    cd portal-proto
You'll need to set up your Wikidata user name and password credentials, these can be exported as environment variables for now along with another variable that sets the flask app name:

     export WIKIDP_BOT_USER='<username>'
     export WIKIDP_BOT_PASSWORD='<password>'
     export FLASK_APP='wikidp'
where `<username>` and `<password>` are your username and password. **NOTE** *these will need to be set for every new session for now*. Finally install and run the  Flask application:

    pip install -e .
    flask run
    
Point your browser to http://127.0.0.1:5000 and you should see the prototype of the portal.

Troubleshooting
--------------
#### Set FLASK_APP env variable
If you see something like:

    Usage: flask run [OPTIONS]

    Error: Could not locate Flask application. You did not provide the FLASK_APP environment variable.

    For more information see http://flask.pocoo.org/docs/latest/quickstart/
You need to set the FLASK_APP environment variable, see Quick Start above.
