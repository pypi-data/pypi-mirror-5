======
Tigger
======

Tigger is a command-line tagging tool written in python, intended for tracking
tags on files in a form which can be transferred with the files while remaining
out of sight normally (much like git's metadata, except not so clever).

Installation
============

Lines preceded with # should be run as root, unless installing in a virtualenv.
Lines preceded with $ should be run as your normal user.

You can install the module via pip::

    # pip install tigger

Or from a clone of the source::

    $ git clone https://github.com/bit-shift/tigger
    $ cd tigger
    # ./setup.py install

Usage
=====

tigger has a number of distinct functions (with more to be added as a need for
them is found), each available as one subcommand:

Tagging
-------

Syntax::

    tigger tag -t TAG [-t TAG ...] FILE [FILE ...]

Applies all given tags (``TAG``) to all given files (``FILE``).

Untagging
---------

Syntax::

    tigger untag -t TAG [-t TAG ...] FILE [FILE ...]

Removes all given tags (``TAG``) from all given files (``FILE``).

Listing tags
------------

Syntax::

    tigger tags FILE [FILE ...]

Lists all tags on each ``FILE``.

Listing files
-------------

Syntax::

    tigger files TAG [TAG ...]

Lists all files belonging to each tag.
