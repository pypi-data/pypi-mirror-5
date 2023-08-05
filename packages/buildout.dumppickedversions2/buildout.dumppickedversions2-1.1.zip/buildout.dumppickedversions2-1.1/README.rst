buildout.dumppickedversions2
============================

``buildout.dumppickedversions2`` is a simple buildout extension
that mimicks the features of ``buildout.dumppickedversions`` for
buildout version 2.0.1 or later.

The problem and it's solution
-----------------------------

After upgrading buildout to version 2 you'll notice that use of
``buildout.dumppickedversions`` has been disabled. This has been
done because part of the features of ``buildout.dumppickedversions``
have been integrated into buildout.

However the overwriting behavior of ``buildout.dumppickedversions``
has not been integrated. This extension monkey patches the built-in 
version dumping so it behaves more like ``buildout.dumppickedversions``.

An added benefit is that the configuration options haven't been
changed. This means that upgrading you buildout file is a simple 
addition of the number two to ``extensions = buildout.dumppickedversions``.

``buildout.dumppickedversions2`` requires zc.buildout 2.0.1 or later.

buildout.dumppickedversions2 options
------------------------------------

dump-picked-versions-file
    A file name you want ``buildout.dumppickedversions`` to write to.
    If not given ``buildout.dumppickedversions`` will dump the versions to the 
    screen. The latter behavior is now built into buildout and can be enabled
    without an extension by setting ``show-picked-versions`` to ``true``.

overwrite-picked-versions-file
    If set to ``true``, ``buildout.dumppickedversions`` will overwrite the file 
    defined in ``dump-picked-versions-file`` if it exists. This value
    defaults to True.
