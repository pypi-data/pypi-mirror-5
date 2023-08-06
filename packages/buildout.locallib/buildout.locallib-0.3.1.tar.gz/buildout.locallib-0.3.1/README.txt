`buildout.locallib` use egg-packages installed on site-packages folder.

`zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ check
package installation by zc.buildout.easy_install.Installer that
exclude /path/to/site-packages folder path for checking.

When 'site-packages' folder include some easy-installed packages,
We want to re-use these packages in some cases.

Features
--------

* Extends zc.buildout functionality to search installed packages.
* create dummy '*.egg-info' / '*.egg-link' for specified packages.


Using sample: using buildout.locallib extension
-------------------------------------------------

site-packages include some eggs::

   $ ls /path/to/site-packages
   easy-install.pth
   pip-0.6.3-py2.6.egg/
   pastedeploy-1.3.3-py2.6.egg/
   pastescript-1.7.3-py2.6.egg/
   paste-1.7.4-py2.6.egg/
   setuptools-0.6c11-py2.6.egg
   setuptools.pth


write buildout.cfg::

   [buildout]
   parts = foo

   [foo]
   recipe = zc.recipe.egg
   eggs =
       PasteScript


run bootstrap and buildout::

   $ python bootstrap.py
   $ bin/buildout -U
   ...

list eggs dir::

   $ ls eggs
   zc.recipe.egg-1.2.3b2-py2.6.egg
   pastescript-1.7.3-py2.6.egg
   pastedeploy-1.3.3-py2.6.egg
   paste-1.7.4-py2.6.egg

(clean-up)::

   $ rm -R eggs

Now update buildout.cfg to use ``buildout.locallib`` extension::

   [buildout]
   parts = foo
   extensions = buildout.locallib
   ...

And run buildout again::

   $ bin/buildout -U
   ...

Check your eggs folder again::

   $ ls eggs
   buildout.locallib-0.0.1-py2.6.egg
   zc.recipe.egg-1.2.3b2-py2.6.egg

If package exists at site-packages folder, now using installed version
packages.


Using sample: specified dummy package information
--------------------------------------------------

site-packages include some libraries, but they are not installed by easy_insttall::

   $ ls /path/to/site-packages
   ...
   feedparser.py
   ...

write buildout.cfg with ``locallibs`` key and section::

   [buildout]
   parts = foo
   newest = false #if you won't want to check newest version (network-access)
   extensions = buildout.locallib
   locallibs = locallibs

   [foo]
   recipe = zc.recipe.egg
   eggs =
       feedparser

   [locallibs]
   feedparser = feedparser==4.1

``locallibs`` section require ``(dummy name) = (pkg name)==(version)`` style
key-value pairs. Then, buildout.locallib create dummy ``feedparser-4.1.egg-info``
into the develop-eggs directory. In this way, setuptools recognizes that a
'feedparser' is installed and doesn't perform downloading.

If target package have .egg-info file/directory, you don't need to write
a `version` like below::

   [locallibs]
   PIL = PIL

But, if you omit a version for no-egg-info package, buildout.locallib can't
recognize package version, then it'll cause DistributionNotFound exception.
If you want to avoid this exception, you should set `locallibs_check = false`
in buildout section.

Options
--------
locallibs
   A dictionary mapping package names to skip installing distribution
   that was installed on python's site-packages directory already.
   This can be used to specify a set of distribution versions independent
   of other requirements.

locallibs_check
   default is 'true'. buildout.locallib check distribution existing on
   site-packages and raise exception if distribute was not found.
   If set 'false', skip check.


Requirements
------------

* Python 2.4 or later


Dependencies
------------

* `setuptools <http://pypi.python.org/pypi/setuptools>`_ or
  `distribute <http://pypi.python.org/pypi/distribute>`_

* `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_


Setup
-----

Write buildout.cfg with `extensions = buildout.locallib`::

   [buildout]
   parts = foo
   extensions = buildout.locallib
   ...


ToDo
-----
* Write tests.
* cleanup develop-eggs folder.


History
-------

0.3.1 (2013-8-18)
~~~~~~~~~~~~~~~~~~
* Fix: create develop-eggs directory if missing.

0.3.0 (2011-3-31)
~~~~~~~~~~~~~~~~~~
* Add: locallibs_check option is now available.

0.2.0 (2010-7-12)
~~~~~~~~~~~~~~~~~~
* Add: create dummy '*.egg-info' / '*.egg-link' for specified packages.

0.1.0 (2010-6-27)
~~~~~~~~~~~~~~~~~~
* first release

