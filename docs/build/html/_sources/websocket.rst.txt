Websocket Server
================

In the server folder are three files to get started. It is only an example
server, but if you want to run it, you'll need a ``MySQL`` server running, as
well as ``nodejs`` installed.

Import ``database.sql`` in the database, and modify the ``index.js`` file to
put in the login information for the database. Then, simply run in the folder::

    $ node install
    ...
    $ node index.js


Don't forget to set the right address on the websocket parameter. Once
activated, the trainer will send the information right to the server and fill
the database.
