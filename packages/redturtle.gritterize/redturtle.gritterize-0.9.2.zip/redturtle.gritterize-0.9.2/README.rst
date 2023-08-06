====================
redturtle.gritterize
====================

A Plone add-on that makes the standard Plone status messages
appear like a Growl notification using the
`jQuery Gritter plugin <http://boedesign.com/blog/2009/07/11/growl-for-jquery-gritter/>`_.

* `Source code @ GitHub <https://github.com/RedTurtle/redturtle.gritterize>`_
* `Releases @ PyPI <https://pypi.python.org/pypi/redturtle.gritterize>`_
* `Documentation @ ReadTheDocs <http://redturtlegritterize.readthedocs.org>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/RedTurtle/redturtle.gritterize>`_

It transforms the Plone status messages from this

.. figure:: http://blog.redturtle.it/pypi-images/redturtle.gritterize/ungritterized.png/image_preview
   :alt: The default Plone messages

to this

.. figure:: http://blog.redturtle.it/pypi-images/redturtle.gritterize/gritterized.png/image_preview
   :alt: The gritterized Plone messages

How it works
============
**It just works**!
If JavaScript is disabled you will have
the standard Plone behaviour.
Test it visiting:

- http://localhost:8080/Plone/@@test-redturtle-gritterize

Installation
============

To install `redturtle.gritterize` you simply add ``redturtle.gritterize``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `redturtle.gritterize` using the Add-ons control panel.


Configuration
=============

At the moment it is really basic, **this will change**.
You can configure the stickiness and the persistence time (in milliseconds)
by adding a custom a config object to the igritter global object::

  igritter.config = {
      time: {
        'portalMessage info': 10000,
        'portalMessage warning': 20000,
      }
  };

According to the matching portal message class the right persistnece time
will be set (in this case 10 seconds for the info ones,
20 for the warning ones).
If the lookup fails the gritter message will be sticky.

