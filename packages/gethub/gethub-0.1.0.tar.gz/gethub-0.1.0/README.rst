gethub
======

Clones (aka "gets") all of your GitHub repos.

Installation
------------

Clone the repo and add ``bin/gethub`` to your ``$PATH``, or install via
``pip``:

::

    $ pip install gethub

Usage
-----

Clone all public repos:

::

    $ gethub -u <user>

OR

::

    $ gethub -a # leave the password blank when prompted

Clone private repos:

::

    $ gethub -u <user>:<password>

OR

::

    $ gethub -a # fill in the password when prompted

You can optionally clone gists instead of repos by adding a ``-g`` flag.
