rt.ploneversions
================

Retrieve information from dist.plone.org to safely
and easily pin your egg versions.

Motivation
----------

It is a common practice, for Plone buildouts,
to extend online configuration files
that declare known good working versions.
Those external resources can, in turn,
extend other remote resources.

This means that your buildout relies on the assumption
that the all those external resources are available.
If they are not buildout will fail:
a network problem can really turn out in a catastrophe!

This already happened. Luckily there are workarounds to solve this issue:

- http://devblog.4teamwork.ch/blog/2013/06/06/download-dot-zope-dot-org-is-down-how-to-fix-buildout/

Another (minor) issue with this approach is that
you have to wait for the resources to be fetched
before starting.

Some other times, you may not want to include network resources,
e.g. because your customer network will not easily allow you
to fetch them.

Given that I don't want to cross my finger
and wait for those resources to be retrieved on the net,
I started including all those externals
known good working versions in a file.

It is tedious to do it by hand,
because you have to fetch and merge some files in the correct order,
so I wrote the `ploneversions` script.

I hope you will enjoy it!

Installation
------------

You can install **rt.ploneversions** with pip or easy_install::

    pip install rt.ploneversions

Usage
-----

Launch the `ploneversions` script
passing a valid Plone version.

Example output (with some ellipses)::

    $ ploneversions 4.3-latest
    ## http://download.zope.org/zopetoolkit/index/1.0.8/zopeapp-versions.cfg
    zope.app.applicationcontrol = 3.5.10
    ...
    zope.rdb = 3.5.0

    ## http://download.zope.org/zopetoolkit/index/1.0.8/ztk-versions.cfg
    zope.annotation = 3.5.0
    ...
    zope.kgs = 1.2.0

    ## http://download.zope.org/Zope2/index/2.13.21/versions.cfg
    Zope2 = 2.13.21
    ...
    zope.testbrowser = 3.11.1

    ## http://dist.plone.org/release/4.3-latest/versions.cfg
    docutils = 0.9.1
    ...
    zc.relation = 1.0

You may want to redirect this output to a file, e.g.::

    $ ploneversions 4.3-latest > versions.cfg

and add this file to your buildout.

You can check the available Plone versions here http://dist.plone.org/release.


Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

