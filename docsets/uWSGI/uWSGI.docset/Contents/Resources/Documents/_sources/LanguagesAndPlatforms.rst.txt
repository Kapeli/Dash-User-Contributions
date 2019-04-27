Supported languages and platforms
=================================

.. list-table:: 
    :header-rows: 1
    
    * - Technology
      - Available since
      - Notes
      - Status
    * - Python
      - 0.9.1
      - The first available plugin, supports WSGI (:pep:`333`, :pep:`3333`),
        Web3 (from version 0.9.7-dev) and Pump (from 0.9.8.4). Works with
        :doc:`Virtualenv`, multiple Python interpreters, :doc:`Python3` and
        has unique features like :doc:`PythonModuleAlias`,
        :doc:`DynamicVirtualenv` and :doc:`uGreen`. A module exporting handy
        :doc:`decorators<PythonDecorators>` for the uWSGI API is available in
        the source distribution. PyPy :doc:`is supported<PyPy>` since 1.3. The
        :doc:`Tracebacker` was added in 1.3.
      - Stable, 100% uWSGI API support
    * - Lua
      - 0.9.5
      - Supports :doc:`LuaWSAPI`, coroutines and threads
      - Stable, 60% uWSGI API support
    * - Perl
      - 0.9.5
      - :doc:`Perl` (PSGI) support. Multiple interpreters, threading and async
        modes supported
      - Stable, 60% uWSGI API support
    * - Ruby
      - 0.9.7-dev
      - :doc:`Ruby` support. A loop engine for :doc:`Ruby 1.9
        fibers<FiberLoop>` is available as well as a handy :doc:`DSL <RubyDSL>`
        module.
      - Stable, 80% uWSGI API support
    * - :doc:`Erlang`
      - 0.9.5
      - Allows message exchanging between uWSGI and Erlang nodes.
      - Stable, no uWSGI API support
    * - :doc:`CGI`
      - 1.0-dev
      - Run CGI scripts
      - Stable, no uWSGI API support
    * - :doc:`PHP`
      - 1.0-dev
      - Run PHP scripts
      - Stable from 1.1, 5% uWSGI API support   
    * - :doc:`Go`
      - 1.4-dev
      - Allows integration with the Go language
      - 15% uWSGI API support
    * - :doc:`JVM`
      - 1.9-dev
      - Allows integration between uWSGI and the Java Virtual Machine
        :doc:`JWSGI<JWSGI>` and :doc:`Clojure/Ring<Ring>` handlers are available.
      - Stable
    * - :doc:`Mono`
      - 0.9.7-dev
      - Allows integration between uWSGI and Mono, and execution of ASP.NET
        applications.
      - Stable
    * - :doc:`V8`
      - 1.9.4
      - Allows integration between uWSGI and the V8 JavaScript engine.
      - Early stage of development
