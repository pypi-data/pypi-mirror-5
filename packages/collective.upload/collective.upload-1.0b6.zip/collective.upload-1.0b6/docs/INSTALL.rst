Installation
------------

To enable this product in a buildout-based installation:

1. Edit your buildout.cfg and add ``collective.upload`` to the list of eggs to
   install::

    [buildout]
    ...
    eggs =
        collective.upload

2. If you're using Plone 4.2, you may need to pin the right versions of the
   jQuery and jQuery Tools packages::

    [versions]
    plone.app.jquery = 1.7.2
    plone.app.jquerytools = 1.5.5

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ``collective.upload`` and click the 'Activate' button.

Note: You may have to empty your browser cache and save your resource
registries in order to see the effects of the product installation.
