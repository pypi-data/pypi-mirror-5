================
gunicorn-console
================

Created by `Stephen McDonald <http://twitter.com/stephen_mcd>`_

A curses application for managing gunicorn processes. The ``ps`` command is 
polled for gunicorn processes named with the ``setproctitle`` package and its 
output is parsed to display a list of gunicorn processes showing the process 
ID, port, name, rough memory used and number of workers for each gunicorn. 
A gunicorn in the list can then be selected and several operations are 
supported via keypresses such as modifying the number of worker process per 
gunicorn as well as reloading or shutting down the master gunicorn process.

Dependencies
============

  * `setproctitle <http://pypi.python.org/pypi/setproctitle>`_

.. image:: http://media.tumblr.com/tumblr_l35pgbDlII1qa0qji.gif
