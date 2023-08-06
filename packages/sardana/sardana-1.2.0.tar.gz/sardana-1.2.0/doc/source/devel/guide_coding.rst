.. _sardana-coding-guide:

==============================
Sardana development guidelines
==============================

Overview
---------

This document describes sardana from the perspective of developers. Most 
importantly, it gives information for people who want to contribute to the 
development of sardana. So if you want to help out, read on!

How to contribute to sardana
----------------------------

Sardana development is managed with the `Sardana sourceforge project
<https://sourceforge.net/projects/sardana/>`_. Until release 1.2, a svn
repository has been used to host the source code. From then on, the version
control will be moved to a git repository.

How to checkout sardana from SVN
--------------------------------

.. warning:: These instructions will become obsolete as soon as Sardana 1.2 
             is released because the code development will be moved from SVN to
             Git. Updated instructions for using Git will be posted ASAP.

**For read-only**::

    svn co https://svn.code.sf.net/p/sardana/code/trunk Sardana

**To being able to commit**::

    svn co https://<user name>@svn.code.sf.net/p/sardana/code/trunk Sardana

.. note::
    
    You must have a sourceforge user account and have SVN write
    access to the tango-cs project. You can ask write access to any of the 
    tango-cs project administrators.


Documentation
-------------

All standalone documentation should be written in plain text (``.rst``) files
using reStructuredText_ for markup and formatting. All such
documentation should be placed in directory :file:`docs/source` of the sardana
source tree. The documentation in this location will serve as the main source
for sardana documentation and all existing documentation should be converted
to this format.

Coding conventions
------------------

* In general, we try to follow the standard Python style conventions as
  described in
  `Style Guide for Python Code  <http://www.python.org/peps/pep-0008.html>`_
* Code **must** be python 2.6 compatible
* Use 4 spaces for indentation
* In the same file, different classes should be separated by 2 lines
* use ``lowercase`` for module names. If possible prefix module names with the
  word ``sardana`` (like :file:`sardanautil.py`) to avoid import mistakes.
* use ``CamelCase`` for class names
* python module first line should be::

    #!/usr/bin/env python
* python module should contain license information (see template below)
* avoid poluting namespace by making private definitions private (``__`` prefix)
  or/and implementing ``__all__`` (see template below)
* whenever a python module can be executed from the command line, it should 
  contain a ``main`` function and a call to it in a ``if __name__ == "__main__"``
  like statement (see template below)
* document all code using Sphinx_ extension to reStructuredText_

The following code can serve as a template for writting new python modules to
sardana::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    ##############################################################################
    ##
    ## This file is part of Sardana
    ## 
    ## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
    ##
    ## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
    ## 
    ## Sardana is free software: you can redistribute it and/or modify
    ## it under the terms of the GNU Lesser General Public License as published by
    ## the Free Software Foundation, either version 3 of the License, or
    ## (at your option) any later version.
    ## 
    ## Sardana is distributed in the hope that it will be useful,
    ## but WITHOUT ANY WARRANTY; without even the implied warranty of
    ## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    ## GNU Lesser General Public License for more details.
    ## 
    ## You should have received a copy of the GNU Lesser General Public License
    ## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
    ##
    ##############################################################################

    """A :mod:`sardana` module written for template purposes only"""

    __all__ = ["SardanaDemo"]
    
    __docformat__ = "restructuredtext"
    
    class SardanaDemo(object):
        """This class is written for template purposes only"""
        
    def main():
        print "SardanaDemo"
    
    if __name__ == "__main__":
        main()


.. _Tango: http://www.tango-controls.org/
.. _tango_cs: https://sourceforge.net/projects/tango-cs/
.. _reStructuredText:  http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org/
