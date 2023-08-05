Example usage
=============

Some needed imports::

    >>> import re
    >>> import os
    >>> import time
    >>> from multiprocessing.connection import Client

We'll start by creating a simple ``buildout.cfg`` that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logger
    ... # For some reason this is now needed:
    ... index = http://b.pypi.python.org/simple
    ... newest = false
    ...
    ... [logger]
    ... recipe = collective.recipe.logger
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Getting distribution for 'zc.recipe.egg'.
    Got zc.recipe.egg 1.3.2.
    Installing logger.
    Generated script '/sample-buildout/bin/logger'.
    <BLANKLINE>

Let's test the daemon::

    >>> print system('bin/logger start')
    Starting...
    <BLANKLINE>

    >>> status_info = system('bin/logger status')
    >>> bool(re.match('Daemon \(pid=\d+\) is already running', status_info))
    True

    >>> print system('bin/logger stop')
    Stopping...
    Stopped
    <BLANKLINE>

Set up more complex example::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = logger
    ... # For some reason this is now needed:
    ... index = http://b.pypi.python.org/simple
    ... newest = false
    ...
    ... [logger]
    ... recipe = collective.recipe.logger
    ... ip = 127.0.0.1
    ... port = 8091
    ... maxlen = 10
    ... format = json
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Uninstalling logger.
    Installing logger.
    Generated script '/sample-buildout/bin/logger'.
    <BLANKLINE>

Let's run the daemon::

    >>> print system('bin/logger start')
    Starting...
    <BLANKLINE>

Send some data to the logger::

    >>> conn = Client(('localhost', 8091))
    >>> conn.send("storage1")

Store file ('test') into the folder ('storage') and open a new storage::

    >>> conn.send(None)

Send one more portion of data::

    >>> conn.send("storage2")

Check whether the file ('test') was stored::

    # wait for creating file
    >>> time.sleep(1)
    >>> len(os.listdir(join(sample_buildout, 'parts/logger/storage'))) == 1
    True

Stop daemon::

    >>> print system('bin/logger stop')
    Stopping...
    Stopped
    <BLANKLINE>

