=========
 filespy
=========

.. image:: https://travis-ci.org/localvoid/py-filespy.png?branch=master

FileSpy is a simple library that helps you detect filesystem changes.


API
===

CHANGE_TYPE
-----------

``CREATED = 0``

``DELETED = 1``

``MODIFIED = 2``

make_snapshot
-------------

``make_snapshot(path, followlinks=False) -> dict()``

``path`` - directory path

``followlinks=False`` - follow links when traversing through directory

Creates a directory snapshot. Snapshot doesn't hold any information
about directory in which this snapshot was done, so you can easily
compare directories in a different locations.

It returns a simple dictionary, where keys is a file path and value is
os.stat() of this file. It is done in a such way to make serialization
of this data as simple as possible.

snapshot_diff
-------------

``snapshot_diff(s1, s2) -> tuple(CHANGE_TYPE, path)``

Generator that yields changes between two snapshots.


Example
=======

.. code:: python

    s1 = filespy.make_snapshot('/dir')
    time.sleep(3)
    s2 = filespy.make_snapshot('/dir')
    for t, path in filespy.snapshot_diff(s1, s2):
        if t == filespy.CREATED:
            on_create(path)
        elif t == filespy.DELETED:
            on_delete(path)

Here we are taking snapshot of the directory ``/dir``, then sleep for
3 seconds, take another snapshot, and finally looking at the changes.
