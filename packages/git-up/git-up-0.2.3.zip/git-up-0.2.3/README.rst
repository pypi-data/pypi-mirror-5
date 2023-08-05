PyGitUp |Build Status|
======================

``PyGitUp`` is a Python implementation of the great
`aanand/git-up/ <https://github.com/aanand/git-up/>`__. Right now it
fully covers the abilities of git-up and should be a drop-in
replacement.

Why using ``git up``?
---------------------

    git pull has two problems:

    * It merges upstream changes by default, when it's really more polite to `rebase over them <http://gitready.com/advanced/2009/02/11/pull-with-rebase.html>`__, unless your collaborators enjoy a commit graph that looks like bedhead.

    * It only updates the branch you're currently on, which means git push will shout at you for being behind on branches you don't particularly care about right now.

    (https://github.com/aanand/git-up/)

Why using the Python port?
--------------------------

I wasn't able to use the original ``git-up``, because I didn't want to install
a whole Ruby suite just for `git-up` and even with Ruby installed, there were
some problems running on my Windows machine. So, my reasons for writing
and using this port are:

1. Windows support.
2. Written in Python ;)

Is it stable?
-------------

Yes, it should be stable now. If you nevertheless find errors, please
report them `here <https://github.com/msiemens/PyGitUp/issues>`__.

How do I install it?
--------------------

1. Run ``$ pip install git-up``
2. ``cd`` to your project's directory.
3. Run ``git up`` enjoy!

Note for Windows users:
~~~~~~~~~~~~~~~~~~~~~~~

You need ``pip`` installed and working. Check out
`SO#4750806 <http://stackoverflow.com/q/4750806/997063>`__ for more
information. And don't forget to either:

- make your ``Python/Scripts`` and ``Python/Lib/site-packages`` writable for
  you,
- run ``pip`` with admin privileges
- or use ``pip install --user git-up`` and add ``%APPDATA%/Python/Scripts``
  to %PATH%

otherwise ``pip`` won't install due to ``Access denied`` errors.

Compatibility note:
~~~~~~~~~~~~~~~~~~~

``PyGitUp`` is not compatible with Python 3 because some essential 3rd party
libs don't support it. Sorry.

How to configure it?
--------------------

To configure ``PyGitUp``, you can set options in your git config. Run
``git config [--global] git-up.[name] [value]`` to set one of these
options:

-  ``git-up.bundler.check [true|*false*]:`` If set to
   ``true``,\ ``PyGitUp`` will check your app for any new bundled gems
   and suggest a ``bundle install`` if necessary.

-  ``git-up.bundler.autoinstall [true|*false*]:`` If set to
   ``true``,\ ``PyGitUp`` will run ``bundle install`` automatically.
   Requires ``git-up.bundler.check`` to be true.

-  ``git-up.bundler.local [true|*false*]:`` If you've ``bundle package``-ed
   your  project gems, you can tell ``PyGitUp`` to run ``bundle install
   --local`` for you if it finds missing gems. Much faster than just a plain
   old ``bundle install``. Don't worry if you're missing gems, it will
   backtrack to ``bundle install`` if anything goes wrong. Make sure
   ``git-up.bundler.autoinstall`` is also set to ``true`` or it won't do
   anything.

- ``git-up.bundler.rbenv [true|false]:`` If you have rbenv installed,
  you can tell ``PyGitUp`` to run ``rbenv rehash`` for you after it installs
  your gems so any binaries will be available right away. Make sure ``git-up
  .bundler.autoinstall`` is also set to ``true`` or it won't do anything.

-  ``git-up.fetch.prune [*true*|false]:`` If set to ``true``,
   ``PyGitUp`` will append the ``--prune``\ option to ``git fetch`` and
   thus removing any remote tracking branches which no longer exist on
   the remote (see `git fetch
   --help <http://linux.die.net/man/1/git-fetch>`__).

-  ``git-up.fetch.all [true|*false*]:`` If set to ``false``, ``PyGitUp``
   will only fetch remotes for which there is at least one local
   tracking branch. Setting this option will it ``git up`` always fetch
   from all remotes, which is useful if e.g. you use a remote to push to
   your CI system but never check those branches out.

-  ``git-up.rebase.arguments [string]:`` If set, ``PyGitUp`` will use
   this string as additional arguments when calling ``git rebase``.
   Example: ``--preserve-merges`` to recreate merge commits in the
   rebased branch.

-  ``git-up.rebase.auto [*true*|false]:`` If set to ``false``,
   ``PyGitUp`` won't rebase your branches for you but notify you that
   they diverged. This can be useful if you have a lot of in-progress
   work that you don't want to deal with at once, but still want to
   update other branches.

-  ``git-up.rebase.log-hook [cmd]:`` Runs ``cmd``\ every time a branch
   is rebased or fast-forwarder, with the old head as ``$1`` and the new
   head as ``$2``. This can be used to view logs or diffs of incoming
   changes. Example:
   '``echo "changes on $1:"; git log --oneline --decorate $1..$2``\ '

Credits
-------

The original ``git-up`` has been written by aanand:
`aanand/git-up/ <https://github.com/aanand/git-up/>`__.


Changelog
---------

v0.2.3 (*2013-06-05*)
~~~~~~~~~~~~~~~~~~~~~

- Fixed issue `#4 <https://github.com/msiemens/PyGitUp/issues/4>`__ (ugly
  exception if remote branch has been deleted).

v0.2.2 (*2013-05-04*)
~~~~~~~~~~~~~~~~~~~~~

- Fixed issue `#3 <https://github.com/msiemens/PyGitUp/issues/3>`__ (didn't
  return to previous branch).


v0.2.1 (*2013-03-18*)
~~~~~~~~~~~~~~~~~~~~~

- Fixed problem: check-bundler.rb has not been installed when installing via
  PyPI (problems with setup.py).

v0.2 (*2013-03-18*)
~~~~~~~~~~~~~~~~~~~

- Incorporated `aanand/git-up#41 <https://github
  .com/aanand/git-up/pull/41>`__: Support for ``bundle install --local`` and
  ``rbenv rehash``.
- Fixed issue `#1 <https://github.com/msiemens/PyGitUp/issues/1>`__ (strange
  output buffering when having multiple remotes to fetch from).
- Some under-the-hood improvements.

v0.1 (*2013-03-14*)
~~~~~~~~~~~~~~~~~~~

- Initial Release

.. |Build Status| image:: https://travis-ci.org/msiemens/PyGitUp.png?branch=dev
   :target: https://travis-ci.org/msiemens/PyGitUp
