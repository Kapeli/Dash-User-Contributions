uWSGI 2.0.16
============

[20180210]

Maintenance release

Security
------

- [CVE-2018-6758] Stack-based buffer overflow in core/utils.c:uwsgi_expand_path()

Changes
-------

- Backported early_post_jail plugin hook (Bjørnar Ness)
- Fixed ipv6 suupport for http-socket (James Brown)
- Enable execinfo on DragonFly BSD (Aaron LI)
- Fix inet_ntop buffer size (Orivej Desh)
- Add worker running time metrics (Serge/yasek)
- Backported safe-pidfile, safe-pidfile2 (Nate Coraor)
- Stop using libxml2 by default on osx
- Fixed uwsgi_kvlist_parse signature
- Backport http range fixes from master (Curtis Maloney, Sokolov Yura)
- relicensed mod_proxy_uwsgi to Apache 2.0
- logging: Add ${millis} support to json encode
- plugins/router_xmldir: fixup invalid locale check (Riccardo Magliocchetti)
- Add ssl-verify-depth flag to set the max Client CA chain length (Paul Tagliamonte)
- Allow to override build date (Bernhard M. Wiedemann)
- Python 3 plugin: improved thread names handling (Jyrki Muukkonen, Mark Meyer)
- Added uwsgi_resolve_ip for redis host (ahmbas)
- plugins/gevent: Fix signal handlers (Maslov Alexander)
- Write x509 DER to the uwsgi buffer (Paul Tagliamonte)
- plugin/http: Fix compilation (Melvyn Sopacua)
- Fixed emperor throttling system  (Jeremy Hiatt)
- Fix application loading without Plack after excluding "." from @INC in new Perl versions (Anton Petrusevich)
- Fix MULE MSG QUEUE IS FULL message hint (Eugene Tataurov)
- Build System: support k_minor has a _xxx suffix (TOGO Li)
- Fixed drop-after-* options (Robert DeRose)
- Add mule_send_msg success indicator (Josh Tiras)
- Properly check item size in uwsgi_queue_push (Josh Tiras)
- FastRouter / HTTP Router can now have a 'fallback' key configured
- HTTP Router now supports `post-buffer`, just like FastRouter
- Fix handling of `env` in embedded dict in Python plugin (could cause segfaults in single thread mode)
- Add support for Brotli (.br) with `--static-gzip`
- Back-ported HTTP/1.1 support (--http11-socket) from 2.1

Availability
------------

You can download uWSGI 2.0.16 from https://projects.unbit.it/downloads/uwsgi-2.0.16.tar.gz
