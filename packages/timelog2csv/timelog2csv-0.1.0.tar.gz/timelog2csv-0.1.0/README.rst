***********
TimeLog2CSV
***********

.. image:: https://pypip.in/v/timelog2csv/badge.png
        :target: https://pypi.python.org/pypi/timelog2csv

.. image:: https://pypip.in/d/timelog2csv/badge.png
        :target: https://crate.io/packages/timelog2csv/

.. TODO add drone.io badge

``timelog2csv`` - converts a TimeLog calendar to a CSV file.

TimeLog was a time tracking application for OS X. It stored it's data
using iCal. OS X Mountain Lion (and Mavericks) `dropped some features
<http://blog.mediaatelier.com/mountain-lion-and-timelog/>`_ that TimeLog
needed to talk to iCal. So it's impossible to access the recorded data
because the application won't even start.

But this small tool can help: Export the iCal calendar which you used to
store TimeLog's data. Then use ``timelog2csv`` to convert it to a CSV file.

* Free software: BSD license
* `Documentation <http://timelog2csv.rtfd.org>`_
* `Repository <https://bitbucket.org/keimlink/timelog2csv>`_
* `Issue tracker <https://bitbucket.org/keimlink/timelog2csv/issues?status=new&status=open>`_

Features
========

* Convert an iCal file to CSV
* Filter by project name

Installation
============

At the command line using `pip <http://www.pip-installer.org/>`_::

    $ pip install timelog2csv

Or, if you have `virtualenvwrapper <http://www.doughellmann.com/docs/virtualenvwrapper/>`_ installed::

    $ mkvirtualenv timelog2csv
    $ pip install timelog2csv

Usage
=====

Run ``timelog2csv`` like so to see the help::

    $ timelog2csv -h
