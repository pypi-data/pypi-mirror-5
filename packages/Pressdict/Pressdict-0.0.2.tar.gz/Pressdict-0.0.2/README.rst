=========
pressdict
=========

Pressdict is a compressed key-value store for JSON-serializable objects.

The objects to be stored in the container are JSON-serialized and the resulting string is compressed using zlib. The compressed string is then stored as value for the given key. When accessing the values in the container this process is reversed.


Example of usage
----------------

Pressdict can mostly be used like a normal Python dict::

    from pressdict import Pressdict
    pd = Pressdict()
    pd["test"] = {"key": "value", "key2": 2}
    print pd["test"]


Tests
=====

Testing requires having the nose library (`pip install nose`).
After installation, the package can be tested by executing from
outside the source directory::

    nosetests --exe -v
