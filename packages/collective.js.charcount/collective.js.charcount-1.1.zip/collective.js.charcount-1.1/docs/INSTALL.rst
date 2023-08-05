Installation
=============

 * When you're reading this you have probably already run
   ``easy_install collective.js.charcount``. Find out how to install setuptools
   (and EasyInstall) here:
   http://peak.telecommunity.com/DevCenter/EasyInstall

 * Get `pythonproducts`_ and install it via::

       python setup.py install --home /path/to/instance

   into your Zope instance.

 * Create a file called ``collective.js.charcount-configure.zcml`` in the
   ``/path/to/instance/etc/package-includes`` directory.  The file
   should only contain this::

       <include package="collective.js.charcount" />

.. _pythonproducts: http://plone.org/products/pythonproducts

Alternatively, if you are using zc.buildout and the plone.recipe.zope2instance
recipe to manage your project, you can do this:

 * Add ``collective.js.charcount`` to the list of eggs to install, e.g.:

    [buildout]
    ...
    eggs =
        ...
        collective.js.charcount

  * Tell the plone.recipe.zope2instance recipe to install a ZCML slug:

    [instance]
    recipe = plone.recipe.zope2instance
    ...
    zcml =
        collective.js.charcount

  * Re-run buildout, e.g. with:

    $ ./bin/buildout

You can skip the ZCML slug if you are going to explicitly include the package
from another package's configure.zcml file.

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.js.charcount`` and click the 'Activate' button.

Note: You may have to empty your browser cache and save your resource
registries in order to see the effects of the package installation.
