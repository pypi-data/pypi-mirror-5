.. contents:: Table of Contents
   :depth: 2

ZTFY.webapp
***********

Introduction
------------

ZTFY.webapp is mainly based on BlueBream concepts and packages, but
introduces a few changes and a set of new functionalities ; it's main goal
is to provide a Paster template to create a new ZTFY.blog based web site
in just a few seconds.

More informations about ZTFY packages can be found on
`ZTFY home page <http://www.ztfy.org>`_.

The "webapp" is nothing more than a "configuration container", which
references and configures all packages needed to handle a web site ;
it doesn't provide any real functionality in itself, except those required
to handle the web server in itself.

`BlueBream <http://bluebream.zope.org>`_ -- formerly known as **Zope
3** -- is a web framework written in the Python programming language.

BlueBream is free/open source software, owned by the `Zope Foundation
<http://foundation.zope.org>`_, licensed under the `Zope Public
License <http://foundation.zope.org/agreements/ZPL_2.1.pdf>`_ (BSD
like, GPL compatible license).


Features
--------

Here are the features distinguishing BlueBream from other Python web frameworks:

- BlueBream is built on top of the `Zope Toolkit
  <http://docs.zope.org/zopetoolkit>`_ (ZTK), which has many years of
  experience proving it meets the demanding requirements for stable,
  scalable software.

- BlueBream uses the powerful and familiar Buildout_ building system written in
  Python.
  
- BlueBream employs the Zope Object Database ZODB_, a transactional
  object database, providing extremely powerful and easy to use
  persistence.
  
- BlueBream registers components with Zope Component Markup Language
  (`ZCML <http://www.muthukadan.net/docs/zca.html#zcml>`_), an XML
  based configuration language, providing limitless flexibility.

- BlueBream features the `Zope Component Architecture
  <http://muthukadan.net/docs/zca.html>`_ (ZCA) which implements
  *Separation of concerns* to create highly cohesive reusable
  components (zope.component_).

- BlueBream implements the `WSGI` specification (`Web Server Gateway Interface
  <http://www.wsgi.org/wsgi>`_) with the help of `PasteDeploy
  <http://pythonpaste.org/deploy>`_.

- BlueBream includes a number of well tested components to implement
  common activities.  A few of these are:
  
  - zope.publisher_ publishes Python objects on the web, emphasizing
    `WSGI <http://www.wsgi.org/wsgi>`_ compatibility

  - zope.security_ provides a generic mechanism for pluggable 
    security policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing 
    frameworks 

  - zope.pagetemplate_ is an XHTML-compliant language for developing
    templates

  - zope.schema_ is a schema engine to describe your data models

  - zope.formlib_ is a tool for automatically generating forms from your schemas

.. _Buildout: http://www.buildout.org
.. _ZODB: http://www.zodb.org
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

On top of this, ZTFY provides a few set of additional packages, which allows you
to manage a full web site in just a few minutes, including :

- a complete content management interface (based on z3c.form_)

- an alternate ZMI

- a structured web site, containing sections and articles, blog(s), topics...

- images galleries

- and many more little features, described on `ZTFY home page <http://www.ztfy.org>`_.

You will also find on this web page all informations required to know how
to create and setup a new web site using these packages.

Three simple skins are provided in the default setup, and a "nearly ready to use"
configuration file for Apache2 mod_wsgi_ module is also provided.

.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _mod_wsgi: http://code.google.com/p/modwsgi/


Installation
------------

If you have installed `setuptools
<http://pypi.python.org/pypi/setuptools>`_ or `distribute
<http://pypi.python.org/pypi/distribute>`_ an ``easy_install``
command will be available.  Then, you can install ZTFY.webapp using
``easy_install`` command like this::

  $ easy_install ztfy.webapp

Internet access to `PyPI <http://pypi.python.org/pypi>`_ is required
to perform installation of ZTFY.webapp.

The ``ZTFY.webapp`` distribution provides a quick project
creation tool based on PasteScript templates.  Once ZTFY.webapp is installed,
run ``paster`` command to create the project directory structure.
The ``create`` sub-command provided by paster will show a wizard to
create the project directory structure.

::

  $ paster create -t ztfy.webapp

This will bring a wizard asking details about your new project.  If you provide
a package name and version number, you will get a working application which can
be modified further.  The project name will be used as the egg name. You can
also change the values provided later.

The project name can be given as a command line argument::

  $ paster create -t ztfy.webapp sampleproject

If you provide an option from the command line, it will not be
prompted by the wizard. The other variables are given below, you can
give the values from the command line, if required:

- ``interpreter`` -- Name of the custom Python interpreter

- ``release`` -- The version of ZTFY.webapp

- ``version`` -- The version of your project (eg:- 0.1)

- ``description`` -- One-line description of the package

- ``long_description`` -- Multi-line description (in reStructuredText)

- ``keywords`` -- Space-separated keywords/tags

- ``author`` -- Author name

- ``author_email`` -- Author email

- ``url`` -- URL of the homepage

- ``license_name`` -- License name

If you are in a hurry, you can simply press *Enter/Return* key and
change the values later.  But it would be a good idea, if you provide
a good name for your project.


Usage
-----

The generated package is bundled with Buildout configuration and the
Buildout bootstrap script (``bootstrap.py``).  First you need to
bootstrap the buildout itself::

  $ cd sampleproject
  $ python bootstrap.py

The bootstrap script will install the ``zc.buildout`` and ``distribute``
packages.  Also, it will create the basic directory structure.  Next step is
building the application.  To build the application, run the buildout::

  $ ./bin/buidout

The buildout script will download all dependencies and setup the
environment to run your application.

The most common thing you need while developing an application is
running the server.  ZTFY.webapp uses the ``paster`` command provided by
PasteScript to run the WSGI server.  To run the server, you can pass
the PasteDeploy configuration file as the argument to ``serve``
sub-command as given here::

  $ ./bin/paster serve debug.ini

Once you run the server, you can access it here:
http://localhost:8080/ .  The port number (``8080``) can be changed
from the PasteDeploy configuration file (``debug.ini``).

The second most common thing must be running the test cases.
ZTFY.webapp creates a testrunner using the ``zc.recipe.testrunner``
Buildout recipe.  You can see a ``test`` command inside the ``bin``
directory.  To run test cases, just run this command::

  $ ./bin/test

Sometimes you may want to get the debug shell.  ZTFY.webapp provides a
Python prompt with your application object.  You can invoke the debug
shell like this::

  $ ./bin/paster shell debug.ini

More about the test runner and debug shell will be explained in the
BlueBream Manual.  You can continue reading about BlueBream from the
`documentation site <http://bluebream.zope.org>`_.


Resources
---------

- `ZTFY home page <http://www.ztfy.org>`_

- `Website with documentation <http://bluebream.zope.org>`_

- `Project blog <http://bluebream.posterous.com>`_

- The bugs and issues are tracked at `launchpad
  <https://launchpad.net/bluebream>`_.

- `BlueBream Wiki <http://wiki.zope.org/bluebream>`_

- `PyPI Home <http://pypi.python.org/pypi/bluebream>`_

- `Twitter <http://twitter.com/bluebream>`_

- `Mailing list <https://mail.zope.org/mailman/listinfo/bluebream>`_

- IRC Channel: `#bluebream at irc.freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_

- `Buildbot <http://buildbot.afpy.org/bluebream>`_

- The source code is managed at `Zope reposistory
  <http://svn.zope.org/bluebream>`_.  You can perform a read-only
  checkout of trunk code like this (Anonymous access)::

    svn co svn://svn.zope.org/repos/main/bluebream/trunk bluebream

  You can also `become a source code contributor (committer) after signing a
  contributor agreement
  <http://docs.zope.org/developer/becoming-a-committer.html>`_

  You can see `more details about contributing in wiki
  <http://wiki.zope.org/bluebream/ContributingToBlueBream>`_.
