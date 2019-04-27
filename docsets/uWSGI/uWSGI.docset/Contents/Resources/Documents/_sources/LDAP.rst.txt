Configuring uWSGI with LDAP
===========================

uWSGI can be configured using LDAP. LDAP is a flexible way to centralize
configuration of large clusters of uWSGI servers. 

.. note::

  LDAP support must be enabled while :doc:`building<Build>` uWSGI. The
  `libldap` library is required.


Importing the uWSGIConfig schema
--------------------------------

Running uWSGI with the `--ldap-schema` or `--ldap-schema-ldif` parameter will
make it output a standard LDAP schema (or an LDIF file) that you can import
into your server.

An example LDIF dump
--------------------

This is an LDIF dump of an OpenLDAP server with a `uWSGIConfig` entry, running
a Trac instance.

.. code-block:: ldif

  dn: dc=projects,dc=unbit,dc=it
  objectclass: uWSGIConfig
  objectclass: domain
  dc: projects
  uWSGIsocket: /var/run/uwsgi/projects.unbit.it.sock
  uWSGIhome: /accounts/unbit/tracvenv
  uWSGImodule: trac.web.main:dispatch_request
  uWSGImaster: TRUE
  uWSGIprocesses: 4
  uWSGIenv: TRAC_ENV=/accounts/unbit/trac/uwsgi

Usage
-----

You only need to pass a valid LDAP url to the `--ldap` option.  Only the first
entry returned will be used as configuration.

..
  
  uwsgi --ldap ldap://ldap.unbit.it/dc=projects,dc=unbit,dc=it


If you want a filter with sub scope (this will return the first record under
the tree `dc=projects,dc=unbit,dc=it` with `ou=Unbit`):

..

  uwsgi --ldap ldap://ldap.unbit.it/dc=projects,dc=unbit,dc=it?sub?ou=Unbit


.. attention:
  
  Authentication is currently unsupported.
