Introduction
============

Overview
--------

ityou.astream is an Activity Stream for Plone. It works fine with Plone 4.1. 
With Plone > 4.1 it's not yet tested but should also work.

Installation
------------

**Important**: This product is based in *sqlite3*. You first 
have to install sqlite3 and sqlite3 headers.

On Ubuntu LTS 12.4, you can do this with::

    sudo apt-get install sqlite3 libsqlite3-dev

Configure your buildout.cfg:

    [instance]
    ...
    eggs =
        ityou.astream

For further information please see docs/INSTALL.txt.

Plone configuration
-------------------

After restart of Plone, you have to activate the product in Plone.
Go to the Site Setup, click "add-ons" and select  
"ITYOU ESI - Activity Stream" to activate.  

After activating the product, a new view method 'activities' is 
available. 


Changelog
=========

1.1rc4 (release candidate)
--------------------------

- Initial release
