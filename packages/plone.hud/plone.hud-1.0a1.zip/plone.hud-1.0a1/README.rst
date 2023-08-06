=========
plone.hud
=========

Plone Heads Up Display Framework

* `Source code @ GitHub <https://github.com/plone/plone.hud>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/plone.hud>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/plone/plone.hud>`_


How it works
============

`plone.hud` is framework for heads up display panels. It does not contain
any panels on it's own, this Plone add-on groups all the panels from other
add-ons (like `plone.app.hud <https://github.com/plone/plone.app.hud>`_).

Framework looks for configlets in category `HUD`.
Their browser views must extend plone.hud.panel.HUDPanelView class and
be registered for ``Products.CMFPlone.interfaces.IPloneSiteRoot``.

For further reading or if you would like to create your own panels, look here:
`collective.examples.hud <https://github.com/collective/collective.examples.hud>`_


Installation
============

To install `plone.hud` you simply add ``plone.hud``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `plone.hud` using the Add-ons control panel.


Development
===========

.. sourcecode:: bash

    $ git clone git@github.com/plone/plone.hud
    $ cd plone.hud
    $ make  # this will create bin/buildout, execute it and run tests

    $ make tests  # to run tests

