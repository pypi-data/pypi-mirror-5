Virtual Keyring
===============

:author: Olivier Grisel <olivier.grisel@ensta.org>
:description: Generate rebuildable strong passwords

Oneliner overview::

  domain_password == base62(sha1(master_password + domain_key))[:8]


Goal
----

This utility script helps generate a set of rebuildable domain-specific strong
passwords out of a single easy to remember master password and domain specific
keys such as "login@host".

The generated passwords are strong since they use 8 characters out of a 62
characters long alphabet (lowercase and uppercase letters + digits) that are not
to be found in any dictionary.

You can always re-generate your passwords by taking the base 62 encoding of the
sha1 hash of the concatenation of your master password and domain key.


Install
-------

With pip_::

  $ pip install -U virtualkeyring

.. _pip: http://www.pip-installer.org/en/latest/


Usage
-----

Use the interactive command-line tool ``vkr`` that should now be in your PATH,
and type in you master password and domain key::

  $ vkr
  master password: mysecret
  domain key [e.g. 'login@host']: foobar@example.com
  Your password is available in the clipboard. You have 10s to paste it.


To generate passwords with length larger that 8 chars, for instance for an ssh
key passphrase::

  $ vkr -l 20

To generate passwords for a specific alphabet::

  $ vkr -a 42aAuUTt


Add your ssh key with virtualkeyring
------------------------------------

Add a ssh key to your ssh-agent::

  $ vkr-key

This will use your hostname as domain key. You can also set your domain key in
``~/.virtualkeyring``.

Changes
-------

- 1.6 (2013-07-21): use xerox to copy password to clipboard

- 1.4 (2010-04-01): hashlib support. add vkr-key script

- 1.3 (2008-06-01): add factorized out password fetching from stdin (thanks to gawel)

- 1.2 (2008-05-16): add -l and -a parameters

- 1.1 (2008-02-16) use getpass to read the master password from the keyboard

- 1.0 (2007-11-10) initial relase


