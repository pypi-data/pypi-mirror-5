.. _incr:


Increment the number of processes in a watcher
==============================================

This comment increment the number of processes in a watcher by +1.

ZMQ Message
-----------

::

    {
        "command": "incr",
        "properties": {
            "name": "<watchername>",
            "nb": <nbprocess>
        }
    }

The response return the number of processes in the 'numprocesses`
property::

    { "status": "ok", "numprocesses": <n>, "time", "timestamp" }

Command line
------------

::

    $ circusctl incr <name> [<nb>]

Options
+++++++

- <name>: name of the watcher.
- <nb>: the number of processes to add.
