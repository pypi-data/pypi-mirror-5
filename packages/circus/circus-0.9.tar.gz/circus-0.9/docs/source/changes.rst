History
=======

0.9 - 2013-07-16
----------------

- added [env] sections wildcards
- added global [env] secrtion
- fixed hidden exception when circus-web is not installed - #424
- make sure incr/decr commands really us the nb option - #421
- Fix watcher virtualenv site-packages not in PYTHONPATH
- make sure we dont try to remove more processes than 0 - #429
- updated bootstrap.py - #436
- fixed multiplatform separator in pythonpath virtualenv watcher
- refactored socket close function
- Ensure env sections are applied to all watchers - #437
- added the reloadconfig command
- added circus.green and removed gevent from the core - #441, #452
- silenced spurious stdout & warnings in the tests - #438
- $(circus.env.*) can be used for all options in the config now
- added a before_spawn hook
- correct the path of circusd in systemd service file - #450
- make sure we can change hooks and set streams via CLI - #455
- improved doc
- added a spawn_count stat in watcher
- added min_cpu and min_mem parameters in ResourceWatcher plugin
- added the FQDN information to the arbiter.


0.8.1 - 2013-05-28
------------------

* circusd-stats was choking on unix sockets - #415
* circusd-stats & circushttpd child processes stdout/stderr are now left open
  by default. Python <= 2.7.5 would choke in the logging module in case
  the 2/3 fds were closed - #415
* Now redirecting to /dev/null in the child process instead of closing.
  #417

0.8 - 2013-05-24
----------------

* Integrated log handlers into zmq io loop.
* Make redirector restartable and subsequently more robust.
* Uses zmq.green.eventloop when gevent is detected
* Added support for CIRCUSCTL_ENDPOINT environment variable to circusctl - #396
* util: fix bug in to_uid function - #397
* Remove handler on ioloop error - #398.
* Improved test coverage
* Deprecated the 'service' option for the ResourceWatcher plugin - #404
* removed psutil.error usage
* Added UDP discovery in circusd - #407
* Now allowing globs at arbitrary directory levels - #388
* Added the 'statd' configuration option - #408
* Add pidfile, logoutput and loglevel option to circus configuration file - #379
* Added a tutorial in the docs.
* make sure we're merging all sections when using include - #414
* added pipe_stdout, pipe_stderr, close_child_stderr & close_child_stdout
  options to the Process class
* added close_child_stderr & close_child_stdout options to the watcher


0.7.1 - 2013-05-02
------------------

* Fixed the respawn option - #382
* Make sure we use an int for the timeout - #380
* display the unix sockets as well -  #381
* Make sure it works with the latest pyzmq
* introduced a second syntax for the fd notation


0.7 - 2013-04-08
----------------

* Fix get_arbiter example to use a dict for the watchers argument. #304
* Add some troubleshooting documentation #323
* Add python buildout support
* Removed the gevent and the thread redirectors. now using the ioloop - fixes
  #346. Relates #340
* circus.web is now its own project
* removed the pyzmq patching
* Allow the watcher to be configured but not started #283
* Add an option to load a virtualenv site dir
* added on_demand watchers
* added doc about nginx+websockets #371
* now properly parsing the options list of each command #369
* Fixed circusd-stats events handling #372
* fixed the overflow issue in circus-top #378
* many more things...

0.6 - 2012-12-18
----------------


* Patching protocols name for sockets - #248
* Don't autoscale graphs. #240
* circusctl: add per command help, from docstrings #217
* Added workers hooks
* Added Debian package - #227
* Added Redis, HTTP Observer, Full stats & Resource plugins
* Now processes can have titles
* Added autocompletion
* Added process/watcher age in the webui
* Added SSH tunnel support
* Now using pyzmq.green
* Added upstart script & Varnish doc
* Added environment variables & sections
* Added unix sockets support
* Added the *respawn* option to have single-run watchers
* Now using tox in the tests
* Allow socket substitution in args
* New doc theme
* New rotation options for streams: max_bytes/backup_count


0.5.2 - 2012-07-26
------------------

* now patching the thread module from the stdlib
  to avoid some Python bugs - #203
* better looking circusctl help screen
* uses pustil get_nice() when available (nice was deprecated) - #208
* added max_age support - #221
* only call listen() on SOCK_STREAM or SOCK_SEQPACKET sockets
* make sure the controller empties the plugins list in update_watchers() - #220
* added --log-level and --log-output to circushttpd
* fix the process killing via the web UI - #219
* now circus is zc.buildout compatible for scripts.
* cleanup the websocket when the client disconnect - #225
* fixed the default value for the endpoint - #199
* splitted circushttpd in logical modules


0.5.1 - 2012-07-11
------------------

* Fixed a bunch of typos in the documentation
* Added the debug option
* Package web-requirements.txt properly
* Added a errno error code in the messages - fixes #111

0.5 - 2012-07-06
----------------

* added socket support
* added a listsocket command
* sockets have stats too !
* fixed a lot of small bugs
* removed the wid - now using pid everywhere
* faster tests
* changed the variables syntax
* use pyzmq's ioloop in more places
* now using iowait for all select() calls
* incr/decr commands now have an nbprocess parameter
* Add a reproduce_env option to watchers
* Add a new UNEXISTING status to the processes
* Added the global *httpd* option to run circushttpd as a watcher


0.4 - 2012-06-12
----------------

* Added a plugin system
* Added a "singleton" option for watchers
* Fixed circus-top screen flickering
* Removed threads from circus.stats in favor of zmq periodic callbacks
* Enhanced the documentation
* Circus client now have a send_message api
* The flapping feature is now a plugin
* Every command line tool have a --version option
* Added a statsd plugin (sends the events from circus to statsd)
* The web UI now uses websockets (via socketio) to get the stats
* The web UI now uses sessions for "flash messages" in the web ui

0.3.4 - 2012-05-30
------------------

- Fixed a race condition that prevented the controller
  to cleanly reap finished processes.
- Now check_flapping can be controlled in the configuration.
  And activated/deactivated per watcher.


0.3.3 - 2012-05-29
------------------

- Fixed the regression on the uid handling

0.3.2 - 2012-05-24
------------------

- allows optional args property to add_watcher command.
- added circushttpd, circus-top and circusd-stats
- allowing Arbiter.add_watcher() to set all Watcher option
- make sure the redirectors are re-created on restarts


0.3.1 - 2012-04-18
------------------

- fix: make sure watcher' defaults aren't overrided
- added a StdoutStream class.

0.3 - 2012-04-18
----------------

- added the streaming feature
- now displaying coverage in the Sphinx doc
- fixed the way the processes are killed (no more SIGQUIT)
- the configuration has been factored out
- setproctitle support


0.2 - 2012-04-04
----------------

- Removed the *show* name. replaced by *watcher*.
- Added support for setting process **rlimit**.
- Added support for include dirs in the config file.
- Fixed a couple of leaking file descriptors.
- Fixed a core dump in the flapping
- Doc improvments
- Make sure circusd errors properly when another circusd
  is running on the same socket.
- get_arbiter now accepts several watchers.
- Fixed the cmd vs args vs executable in the process init.
- Fixed --start on circusctl add


0.1 - 2012-03-20
----------------

- initial release
