.. -*- mode: rst -*-

******************
python-liblockfile
******************

A Python wrapper around ``liblockfile``, using ``ctypes``. You must have
the ``liblockfile`` shared library installed on your system. On Ubuntu,
this can be done with::

  sudo apt-get install liblockfile1

For more information see the `Launchpad project page`_.

.. _Launchpad project page: https://launchpad.net/python-liblockfile


Getting started
===============

::

  lockfile = os.path.join(args.output, ".lock")
  with Lock.WithPID(lockfile) as lock, LockHolder(lock):
      ...
