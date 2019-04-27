Glossary
========

.. glossary::
  :sorted:

  harakiri
      A feature of uWSGI that aborts workers that are serving requests for an
      excessively long time. Configured using the ``harakiri`` family of
      options.  Every request that will take longer than the seconds specified
      in the harakiri timeout will be dropped and the corresponding worker
      recycled.

  master
      uWSGI's built-in prefork+threading multi-worker management mode,
      activated by flicking the ``master`` switch on. For all practical serving
      deployments it is generally a good idea to use master mode.
