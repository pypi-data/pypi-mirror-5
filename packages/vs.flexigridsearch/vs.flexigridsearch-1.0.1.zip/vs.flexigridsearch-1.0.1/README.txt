vs.flexigridsearch
==================

``vs.flexigridsearch`` provides a drop-in replacement for the search.pt
template of Plone 3/4.  The search results are presented as a sortable table
using the jQuery ``flexigrid`` plugin.

Installation
------------

* add ``vs.flexigridsearch`` to the ``eggs`` option of your buildout configuration
  and re-run buildout
* create a new Plone site using the related Plone3 or Plone 4 extension profile of 
  ``vs.flexigridsearch``
* or import the related profile for an existing Plone site through ``portal_setup`` 
  (``Import`` tab) (there are dedicatd profiles for Plone 3 and Plone 4 since we
  need different flexigrid versions due to different jQuery versions in Plone 3 and 4).

Usage
-----
* no special usage: perform a search and the result should be rendered using
  the flexgrid jQuery add-on.

Configuration
-------------
* ``vs.flexigridsearch`` uses a property sheet under
  portal_properties/flexigridsearch_properties for its configuration:

  - ``portalTypesToSearch`` - a list of portal types to be searched 
    (a future version of the software will use the configuration of Plone)

  - ``sort_limit`` - maximum number of hits to be retrieved from portal_catalog.
    The parameter name is kind of misleading but the portal_catalog will
    really limit the number of returned rows

  - ``columns`` - defines the columns of the flexigrid table. In general 
    ``vs.flexigridsearch`` can support all searchable indexes of the portal_catalog:

    - Title (this should be always included if you want a clickable link to the content object)
    - Description
    - getId
    - created
    - Creator
    - start
    - end
    - effective
    - expires
    - location
    - Subject
    - getObjSize
    - review_state
    - portal_type

Requirements
------------
* tested with Plone 3.3.X, 4.0.X
* not compatible with Plone 4.2 or higher

Translations
------------

Due to the lack of a proper i18n framework in Plone we provide our own
home-grown i18n translation functionality in
``skins/vs_flexigridsearch/vs_flexigridsearch_translations.js``.  Please add
your translations directly here. If you want to contribute translations for
other languages then please make the changes directly in the collective SVN.

Project page
------------

- http://plone.org//products/vs.flexigridsearch

Bugtracker
----------

- http://plone.org/products/vs.flexigridsearch/issues

SVN
---

- http://svn.plone.org/svn/collective/vs.flexigridsearch/trunk/



Licence
-------
``vs.flexigridsearch`` is published under the GNU Public Licence V 2 (GPL 2)

Authors
-------

| Andreas Jung
| info@zopyx.com
| www.zopyx.com
|
| Veit Schiele
| kontakt@veit-schiele.de
| www.veit-schiele.de
|
