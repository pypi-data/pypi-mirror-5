byu-ws-cli-python
=================

A command-line web service client for calling BYU REST web services.

It handles the authentication work so you don't have to.
It supports URLEncoding and Nonce Encoding.  It also supports WSSession and API Keys.
You can mix and match the encoding and the key type as well.

To install from pypi run

    easy_install byu_ws_cli
or

    pip install byu_ws_cli

Next, you need to setup a file called credentials.py somewhere on your python path with the following contents.

    # this file doesn't go into source control

    key = ''                # your apiKey's wsId
    shared_secret = ''      # your apiKey's sharedSecret
    username = ''           # your BYU netId
    password = ''           # your netId password

Finally, call the script.

    call_byu_ws -h
