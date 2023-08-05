====================
collective.cmisquery
====================

Presentation
============

This package is an extension to `collective.cmisbrowser`. It will let
you enter a custom CMIS query, do the search in the browser and
display the results as a public view.

Installation
============

Update buildout profile
-----------------------

Update your buildout profile to include the following eggs and zcml::

  eggs +=
      ...
      collective.cmisbrowser
      collective.cmisquery
  zcml +=
      ...
      collective.cmisbrowser
      collective.cmisquery

**Important**

When using python 2.4.x you will also need to add *httpsproxy_urllib2*
as an egg.

Run the buildout
----------------

Run the buildout to reflect the changes you made to the profile::

  $ bin/buildout -v

Install the extension
---------------------

The extension can be installed through the ZMI or Plone control panel.

Through the ZMI
~~~~~~~~~~~~~~~

 - Go to the *portal quickinstaller* in the ZMI.

 - Check the extension *collective.cmisquery*.

 - Click the *install* button.

Through the Plone control panel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Go to *Site Setup*.

 - Choose *Add-on products*.

 - Check the extension *collective.cmisquery*.

 - Click the *Install* button.

Add a CMIS Query
================

After installing you will be able to add a *CMIS Query* in your Plone
site from the *Add new...* drop-down menu.
