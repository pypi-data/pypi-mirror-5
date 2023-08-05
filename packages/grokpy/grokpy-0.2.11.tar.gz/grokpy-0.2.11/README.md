# grok-py

The Python client library for the Grok Prediction Service

A note about releases:

Development of Grok client libraries happens internally and
is then released to github master at the same time as we
release server side code. Github master branch can thus
be considered STABLE. 

## Installation

From source (includes sample app):

Click the 'Downloads' link
Click either 'Download as zip' or 'Download as tar.gz'
Unpack into a directory of your choice

    $ sudo python setup.py install

From pip:

    $ sudo pip install grokpy

Dependency (For HTTPS):

    $ sudo pip install certifi

## Run the Sample App

Add your API key to the app

 * Open HelloGrok.py in your favorite editor
 * Insert your API_KEY where it says "YOUR_API_KEY"

OR add your API key to your environment

From the command line:

    $ echo "export GROK_API_KEY=YOUR_API_KEY" >> ~/.bashrc
    $ source ~/.bashrc

Launch the app

    $ python HelloGrok.py
