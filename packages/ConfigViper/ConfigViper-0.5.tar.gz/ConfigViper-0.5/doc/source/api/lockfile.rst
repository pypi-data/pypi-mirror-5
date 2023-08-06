
====================
``lockfile`` Package
====================

.. automodule:: configviper.lockfile
    :members: PortaLocker, lockfile
    :undoc-members:


``posixlocker`` Module
======================

.. automodule:: configviper.lockfile.posixlocker
    :members: PosixPortaLocker
    :undoc-members:


``ctypeslocker`` Module
=======================

..
    Due to ``msvcrt`` and other ``ctypes`` details specific to Windows
    systems, I am not able to use automodule directive nor autoclass here.
    I am thinking in a way to mock those implementations on the documentation
    level without any changes to the ``ctypeslocker`` module, but I cannot
    figure out why.

    So I choose to replicate the doc string text for the ``CTypesPortaLocker``
    class, instead of make changes to the module just to accommodate the
    documentation building requirements.

.. class:: CTypesPortaLocker

    File lock implementation targeting Windows :sup:`TM` based on ``ctypes``
    Python package, using underlying ``LockFileEx`` and ``UnlockFileEx``
    functions.
