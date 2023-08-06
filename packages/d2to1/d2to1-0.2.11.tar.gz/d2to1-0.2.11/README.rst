Introduction
==============
.. image:: https://travis-ci.org/iguananaut/d2to1.png?branch=master
   :alt: travis build status
   :target: https://travis-ci.org/iguananaut/d2to1

d2to1 (the 'd' is for 'distutils') allows using distutils2-like setup.cfg files
for a package's metadata with a distribute/setuptools setup.py script.  It
works by providing a distutils2-formatted setup.cfg file containing all of a
package's metadata, and a very minimal setup.py which will slurp its arguments
from the setup.cfg.

Note: distutils2 has been merged into the CPython standard library, where it is
now known as 'packaging'.  This project was started before that change was
finalized.  So all references to distutils2 should also be assumed to refer to
packaging.

Rationale
===========
I'm currently in the progress of redoing the packaging of a sizeable number of
projects.  I wanted to use distutils2-like setup.cfg files for all these
projects, as they will hopefully be the future, and I much prefer them overall
to using an executable setup.py.  So forward-support for distutils2 is
appealing both as future-proofing, and simply the aesthetics of using a flat text file to describe a project's metadata.

However, I did not want any of these projects to require distutils2 for
installation yet--it is too unstable, and not widely installed.  So projects
should still be installable using the familiar `./setup.py install`, for
example.  Furthermore, not all use cases required by some of the packages I
support are fully supported by distutils2 yet.  Hopefully they will be
eventually, either through the distutils2 core or through extensions.  But in
the meantime d2to1 will try to keep up with the state of the art and "best
practices" for distutils2 distributions, while adding support in areas that
it's lacking.

Usage
=======
d2to1 requires a distribution to use distribute or setuptools.  Your
distribution must include a distutils2-like setup.cfg file, and a minimal
setup.py script.  For details on writing the setup.cfg, see the `distutils2
documentation`_.  A simple sample can be found in d2to1's own setup.cfg (it
uses its own machinery to install itself)::

 [metadata]
 name = d2to1
 version = 0.1.1
 author = Erik M. Bray
 author-email = embray at stsci.edu
 summary = Allows using distutils2-like setup.cfg files for a package's metadata
  with a distribute/setuptools setup.py
 description-file = README
 license = BSD
 requires-dist = setuptools
 classifier =
     Development Status :: 4 - Beta
     Environment :: Plugins
     Framework :: Setuptools Plugin
     Intended Audience :: Developers
     License :: OSI Approved :: BSD License
     Operating System :: OS Independent
     Programming Language :: Python
     Topic :: Software Development :: Build Tools
     Topic :: Software Development :: Libraries :: Python Modules
     Topic :: System :: Archiving :: Packaging
 keywords =
     setup
     distutils
 [files]
 packages = d2to1

The minimal setup.py should look something like this::

 #!/usr/bin/env python

 try:
     from setuptools import setup
 except ImportError:
     from distribute_setup import use_setuptools
     use_setuptools()
     from setuptools import setup

 setup(
     setup_requires=['d2to1'],
     d2to1=True
 )

Note that it's important to specify d2to1=True or else the d2to1 functionality
will not be enabled.  It is also possible to set d2to1='some_file.cfg' to
specify the (relative) path of the setup.cfg file to use.  But in general this
functionality should not be necessary.

It should also work fine if additional arguments are passed to `setup()`,
but it should be noted that they will be clobbered by any options in the
setup.cfg file.

Caveats
=========
- The requires-dist option in setup.cfg is implemented through the
  distribute/setuptools install_requires option, rather than the broken
  "requires" keyword in normal distutils.
- Not all features of distutils2 are supported yet.  If something doesn't seem
  to be working, it's probably not implemented yet.
- Does not support distutils2 resources, and probably won't since it relies
  heavily on the sysconfig module only available in Python 3.2 and up.  This is
  one area in which d2to1 should really be seen as a transitional tool.  I
  don't really want to include a backport like distutils2 does.  In the
  meantime, package_data and data_files may still be used under the [files]
  section of setup.cfg.

.. _distutils2 documentation: http://distutils2.notmyidea.org/setupcfg.html
