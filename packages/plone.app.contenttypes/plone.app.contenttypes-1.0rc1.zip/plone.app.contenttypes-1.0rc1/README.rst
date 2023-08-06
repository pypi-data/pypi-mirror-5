.. contents::

Introduction
============

.. image:: http://jenkins.plone.org/job/plone.app.contenttypes/badge/icon

plone.app.contenttypes offers default content types for Plone based on Dexterity. This package is a replacement for the types in ``Products.ATContenttypes``.

**Warning: plone.app.contenttypes is best used when creating a new site from scratch. Using it on a site with existing content is not recommended if you don't know exactly what you're doing!**

It contains the same types as default Plone does:

* Folder
* Document
* News item
* File
* Image
* Link
* Event (this will be replaced by plone.app.event soon)
* Collection (this already replaces plone.app.collection which is no longer needed then)

The main difference from a users perspective is that these types are extendable through-the-web. This means you can go to the control-panel (``.../@@dexterity-types``) and add or remove fields and behaviors for the existing types.

The aim is to mimick the old default-types as closely as possible, not to change the content-creation experience for editors.

plone.app.contenttypes has been merged into the Plone 5.0 branch and will be shipped with the next Plone release: https://dev.plone.org/ticket/12344


Compatability
=============

plone.app.contenttypes works with Plone 4.1+


Installation
============

Add this line in the eggs section of your ``buildout.cfg``::

    eggs =
        ...
        plone.app.contenttypes

If you have a mixed Plone site with Archetypes content and dexterity content use the extra requirement ``plone.app.contenttypes['at_refs']``.

.. note::

   plone.app.contenttypes 1.0b1 and earlier versions did not include a
   collection type (later versions ship with a collection type). In order to
   be able to use the Dexterity-based collection, you have to pin
   plone.app.collection to 2.0b5.


Installing plone.app.contenttypes in an existing Plone-site
-----------------------------------------------------------

When you try to install plone.app.contenttypes in a existing site you might get the following error::

      (...)
      Module Products.GenericSetup.utils, line 509, in _importBody
      Module Products.CMFCore.exportimport.typeinfo, line 60, in _importNode
      Module Products.GenericSetup.utils, line 730, in _initProperties
    ValueError: undefined property 'schema'

Before installing plone.app.contenttypes you have to reinstall plone.app.collection to update collections to the version that uses Dexterity.


What happens to old content?
----------------------------

The old Archetypes-based content still exists and can be viewed but can't be edited. On installation plone.app.contenttypes removes the type-definitions for the old default-types like this::

    <object name="Document" remove="True" />

You can also migrate the old items to the types provided by plone.app.contenttypes (see the section about migrations).

Uninstalling
------------

To remove plone.app.contenttypes, return full functionality to old content and restore the AT-based default-types you have to install the import step "Types Tool" of the current base profile. Follow the following steps:

* in the ZMI navigate to portal_setup and the tab "import"
* in "Select Profile or Snapshot" leave "Current base profile (<Name of your Plonesite>)" selected. This is usually Products.CMFPlone
* select the Types Tool (usually Step 44)
* click "import selected steps"


Migration
=========

**Warning: Migrations are still in an very early stage and might break your site! plone.app.contenttypes is best used when creating a new site from scratch. Please proceed at your own risk!**

For migrations to work you need at least ``Products.contentmigration = 2.1.3``.

For migration sites use the extra requirement ``plone.app.contenttypes['migrate_atct']``.

This version plone.app.contenttypes comes with migrations for the following use-cases:

* from default Archetypes-based types to plone.app.contenttypes
* from older versions of plone.app.contenttypes to current versions

Migrations that will be will come in the future:

* from old p.a.c.-event to DX-plone.app.event
* from AT-plone.app.event to DX-plone.app.event
* from atct ATEvent to DX-plone.app.event
* from ATTopic to DX-plone.app.collections
* from AT-plone.app.collection to DX-plone.app.collections

Theres already a working migration from atct ATEvent to AT-plone.app.event in the plone.app.event package implemented as an upgrade step.


Migrating Archetypes-based content to plone.app.contenttypes
------------------------------------------------------------

plone.app.contenttypes can migrate the following types:

* Folder
* Document
* News item
* File
* Image
* Link

To migrate existing content go to ``/@@migrate_from_atct``.

TODO:

* LinguaPlone
* Plone-Version older tan 4.1.x need ``plone.app.intid``


Migrating content that is translated with LinguaPlone
-----------------------------------------------------

**Warning: This use-case has not yet been thoroughly tested!***

Since LinguaPlone does not support Dexterity you need to migrate from LinguaPlone to plone.app.multilingual (http://pypi.python.org/pypi/plone.app.multilingual). The migration from Products.LinguaPlone to plone.app.multilingual should happen **before** the migration from Archetypes to plone.app.contenttypes. For details on the migration see http://pypi.python.org/pypi/plone.app.multilingual#linguaplone-migration


Migrating from old versions of plone.app.contenttypes
-----------------------------------------------------

Before version 1.0a2 the content-items did not implement marker-interfaces. They will break in newer versions since the views are now registered for these interfaces (e.g. ``plone.app.contenttypes.interfaces.IDocument``). To fix this you can call the view ``/@@fix_base_classes`` on your site-root.



Migrating content that was extended with archetypes.schemaextender
------------------------------------------------------------------

The migration should warn you if your typs are extended with archetypes.schemaextender. The data contained in these fields will be lost.

You need to implement for each schemaextender an own behavior and modify the whole migration. This is an advanced development task.


How to create a new page with only Dexterity
============================================

You have two options:

**1. By hand**

Installing plone.app.contenttypes remove the types automatically, you only have to remove the existing content (front-page, events, news, members).


**2. Automatically**

If you start from scratch you can want to try using a special branch of Products.CMFPlone that gives you the choice between Dexterity and Archetypes when creating a new site. This way you get a brand new site with

Modify your buildout to automatically pull the branch using mr.developer (http://pypi.python.org/pypi/mr.developer)::

    [buildout]
    extensions = mr.developer
    auto-checkout =
        Products.CMFPlone
        Products.ATContentTypes

    [sources]
    Products.CMFPlone = git https://github.com/plone/Products.CMFPlone.git branch=plip-12344-plone.app.contenttypes
    Products.ATContentTypes = git https://github.com/plone/Products.ATContentTypes.git branch=davisagli-optional-archetypes


Differences to Products.ATContentTypes
======================================

The image of the News Item is not a field on the contenttype but a behavior that can add a image to any contenttypes (similar to http://pypi.python.org/pypi/collective.contentleadimage)


Dependencies
============

* ``plone.app.dexterity``. Dexterity is shipped with Plone 4.3.x. Version pinns for Dexterity are included in Plone 4.2.x. For Plone 4.1.x you need to pin the correct version for Dexterity in your buildout. See `Installing Dexterity on older versions of Plone <http://developer.plone.org/reference_manuals/external/plone.app.dexterity/install.html#installing-dexterity-on-older-versions-of-plone>`.

* ``plone.app.collection``.


Design descisions
-----------------

TODO


Information for Addon-Developers
--------------------------------

Differences to ATContentTypes Interfaces

How to:

* extend the types ttw or with xml ()
* export a extended CT into a package to overwrite the default
* extend with behaviors
* make types transateable

- Addon-Products that are known to work with p.a.c


.. note::

  For background information see the `initial discussion on the Plone developer mailinglist <http://plone.293351.n2.nabble.com/atcontenttypes-replacement-with-dexterity-td6751909.html>`_ and the `Plone-Conference 2011 sprint documentation <http://piratepad.net/OkuEys2lgS>`_.

License
-------

GNU General Public License, version 2


Roadmap
-------


Contributors
------------

* Philip Bauer <bauer@starzel.de>
* Michael Mulich <michael.mulich@gmail.com>
* Timo Stollenwerk <contact@timostollenwerk.net>
* Peter Holzer <hpeter@agitator.com>
* Patrick Gerken
* Steffen Lindner
* Daniel Widerin
* Jens Klein <jens@bluedynamics.com>

TODO: add all contributors


Thanks to
---------

* The organizers of the Plone-Conference 2011 in San Francisco for a great conference!
* The organizers of the Wine-and-Beer-Sprint in Munich and Capetown in January 2013
* The creators of Dexterity
