========
routelog
========

routelog is a flexible execution-based log processing program and Domain
Specific Language. routelog takes a rules file in the following format::

    /pattern/    command $1 $2

And operates on one or more log files, executing ``command $1 $2`` for all
lines matching the regular expression ``/pattern/`` substituting the first and
second items in the log line for ``$1`` and ``$2`` respectively. A rules file
with the following directive::

    /ERROR/      echo "$*" | mail -s "Error executing ${3%:} on $2 at $1" error@example.com

Would process a log entry like::

    2012-12-07T12:06:11-05:00 server1 program_name: ERROR foo

and send an email to error@example.com with the subject::

    Error executing program_name on server1 at 2012-12-07T12:06:11-05:00'

and the body::

    2012-12-07T12:06:11-05:00 server1 program_name: ERROR foo

Rules files are processed by the routelog program::

    routelog mail-errors.rules /var/log/*.log

The routelog program acts as a filter, passing all log lines to stdout, which
is useful for doing additional processing in a single pipeline::

    routelog mail-errors.rules /var/log/*.log | bzip2 > todays-logs.`date +%s`.bz2

For more on rules files, see ``man 5 routelog``, for more on routelog see
``man 1 routelog``.

Installing
==========

The routelog project lives on github_, and is available via pip_.

.. _github: https://github.com/axialmarket/routelog
.. _pip: https://pypi.python.org/pypi?:action=display&name=routelog

Installing v0.1 From Pip
------------------------

::

    sudo pip install routelog==0.1

Installing v0.1 From Source
---------------------------

::

    wget https://github.com/axialmarket/routelog/archive/routelog-0.1.tar.gz | tar vzxf -
    cd routelog-0.1
    sudo python setup.py install

Usage
=====

::

    routelog [-h|--help] [-c|--comments] [-n|--no-output] rules_file [ log_file [...]]

Optional Arguments
------------------

\-h, --help
  Print an extended usage to stdout and exit.
\-c, --comments
  Treat comments in log lines (anything following a ' #') as arguments, rather
  than ignoring them.
\-n, --no-output
  Suppress the (default) behavior of printing each log line to stdout.

More documentation is available via for the routelog program
(``man 1 routelog``) and routelog rules file formats (``man 5 routelog``)
after install.

License
=======

routelog is made available for use under a 3-clause BSD license (see:
LICENSE.txt in the package).

Authors
=======

Matthew Story (matt.story@axial.net)
