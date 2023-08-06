.. _reloadconfig:


Reload the configuration file
=============================

This command reloads the configuration file, so changes in the
configuration file will be reflected in the configuration of
circus.


ZMQ Message
-----------

::

    {
        "command": "reloadconfig",
    }

The response return the status "ok". If the property graceful is
set to true the processes will be exited gracefully.


Command line
------------

::

    $ circusctl reloadconfig
