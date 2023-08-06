
MiProMan: (My iTerm2 Profile Manager)
=====================================
.. image:: https://badge.fury.io/py/miproman.png
    :target: http://badge.fury.io/py/miproman

*[Infomercial voice]*
    “Hey kids! Are you tired of maintaining those pesky iTerm2 profiles?

    Well look no further because we have just the thing **MiProMan**.

    Adding a new profile with **MiProMan** is easy.
.. code-block:: bash

        $ add_profile server007 --tags "Super Secret Server"

Usage
-----
.. code-block:: bash

    usage: add_profile [-h] [-c COMMAND] [-t [TAGS [TAGS ...]]]
                       [-r STOP | START,STOP] [-p FILE] [-n TEMPLATE_NAME] [-v]
                       [--version]
                       servers [servers ...]

    MiProMan - iTerm2 Profiles Manager for Humans!

    positional arguments:
      servers               Servers to create profiles for.
                            Can use the form server{0:02d} with the range flag to add a range of servers.
                            Skips if server already exists.

    optional arguments:
      -h, --help            show this help message and exit

      -c COMMAND, --command COMMAND
                            The command to run for each profile.
                            Use {0} to refernce the server name in the command.
                            Default: ssh {}

      -t [TAGS [TAGS ...]], --tags [TAGS [TAGS ...]]
                            Tags for the profiles.

      -r STOP | START,STOP, --range STOP | START,STOP
                            If server uses range format add profiles for specified range.
                            Can be provided as a single number or comma separated pair.
                            If single value range starts from 1.
                            Ex. server{0:02d} -r 4 => server01 - server04
                            Ex. server{0:02d} -r 10,20 => server10 - server20

      -p FILE, --profile FILE
                            iTerm2 profile plist.
                            Default: $HOME/Library/Preferences/com.googlecode.iterm2.plist

      -n TEMPLATE_NAME, --template TEMPLATE_NAME
                            iTerm2 profile name to be used as base template for new server entries.
                            Template is required to add new profiles.
                            Default: Default

      -v, --verbose         Increase output verbosity.

      --version             show program's version number and exit

Installation
------------
To install MiProMan, simply:

.. code-block:: bash

    $ pip install miproman

Or, if you choose to build it yourself:

.. code-block:: bash

    $ python setup.py install

Features
--------

- Add new profiles from the console
- Supports python string substitution format for the server and command
- Define default settings in user config to avoid typing oll options
