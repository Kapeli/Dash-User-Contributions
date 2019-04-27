uWSGI 2.0.14
============

[20161003]

Maintenance release

Changes
-------

- backported gevent-early-monkey-patch (jianbin-wei)
- Fixed OpenBSD version check (Pavel Korovin)
- PSGI/Perl cache api fixes (Alexander Demenshin)
- Correctly decode PATH_INFo in router_rewrite plugin (Ben Hearsum)
- add uwsgi.accepting() for chain-reload + worker-override combo (enkore)
- fixed workers killing when in cheaper modes (Shoham Peller)
- added --cgi-safe option (nnnn20430)
- Implemented graceful reload for COROAE plugin (aleksey-mashanov)
- Added --php-fallback2, --php-fallback-qs (Felicity unixwitch)
- Added ipv4in and ipv6in routing rules (Felicity unixwitch)
- Fixed readline support in python3 when working interactively (Anthony Sottile)
- Implement touch-reloading for mules and spoolers (Alexandre Bonnetain)
- add request_start timestamp in stats (Ben Plotnick)
- Fixed double free in uwsgi_routing_func_rewrite (William Orr)
- Various mod_proxy_uwsgi fixes (Ya-Lin Huang)
- support for 'no-answer' in PSGI (Anton Petrusevich)
- added php-constant option (Дамјан Георгиевски [gdamjan])
- added the stdio logger (Дамјан Георгиевски [gdamjan])
- spooler: fix reading inconsistent data (Pavel Patrin)
- Removed -WError from the build procedure (Riccardo Magliocchetti, suggested by Ian Denhardt)
- The usual amount of coverity-based fixes (Riccardo Magliocchetti)

Availability
------------

You can download uWSGI 2.0.14 from https://projects.unbit.it/downloads/uwsgi-2.0.14.tar.gz
