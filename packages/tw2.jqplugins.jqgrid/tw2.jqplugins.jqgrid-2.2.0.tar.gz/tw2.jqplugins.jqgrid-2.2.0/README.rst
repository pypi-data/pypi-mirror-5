tw2.jqplugins.jqgrid
=========================

:Author: Ralph Bean <rbean@redhat.com>

.. comment: split here

.. _toscawidgets2 (tw2): http://toscawidgets.org/documentation/tw2.core/
.. _jQuery Grid Plugin: http://www.trirand.com/jqgridwiki/doku.php

tw2.jqplugins.jqgrid is a `toscawidgets2 (tw2)`_ wrapper for the `jQuery Grid Plugin`_.

Live Demo
---------
Peep the `live demonstration <http://tw2-demos.threebean.org/module?module=tw2.jqplugins.jqgrid>`_.

Links
-----
Get the `source from github <http://github.com/toscawidgets/tw2.jqplugins.jqgrid>`_.

`PyPI page <http://pypi.python.org/pypi/tw2.jqplugins.jqgrid>`_
and `bugs <http://github.com/toscawidgets/tw2.jqplugins.jqgrid/issues/>`_

Description
-----------

`toscawidgets2 (tw2)`_ aims to be a practical and useful widgets framework
that helps people build interactive websites with compelling features, faster
and easier. Widgets are re-usable web components that can include a template,
server-side code and JavaScripts/CSS resources. The library aims to be:
flexible, reliable, documented, performant, and as simple as possible.

The `jQuery Grid Plugin`_ is an Ajax-enabled JavaScript control that
provides solutions for representing and manipulating tabular data on
the web. Since the grid is a client-side solution loading data dynamically
through Ajax callbacks, it can be integrated with any server-side
technology, including PHP, ASP, Java Servlets, JSP, ColdFusion, and Perl.

This module, tw2.jqplugins.jqgrid, provides `toscawidgets2 (tw2)`_ access to
the `jQuery Grid Plugin`_ widget.

Sampling tw2.jqplugins.jqgrid in the WidgetBrowser
--------------------------------------------------

The best way to scope out ``tw2.jqplugins.jqgrid`` is to load its widgets in the
``tw2.devtools`` WidgetBrowser.  To see the source code that configures them,
check out ``tw2.jqplugins.jqgrid/tw2/jqplugins/jqgrid/samples.py``

To give it a try you'll need git, python, and `virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_.  Run::

    $ git clone git://github.com/toscawidgets/tw2.jqplugins.jqgrid.git
    $ cd tw2.jqplugins.jqgrid
    $ mkvirtualenv tw2.jqplugins.jqgrid
    (tw2.jqplugins.jqgrid) $ pip install tw2.devtools
    (tw2.jqplugins.jqgrid) $ python setup.py develop
    (tw2.jqplugins.jqgrid) $ paster tw2.browser

...and browse to http://localhost:8000/ to check it out.
