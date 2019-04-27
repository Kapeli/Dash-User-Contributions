WSGI env behaviour policies
===========================

When using uWSGI two different strategies can be used for allocating/deallocating the WSGI env using either the
``wsgi-env-behaviour`` or ``wsgi-env-behavior`` option:

``cheat``: it preallocates the env dictionary on uWSGI startup and clears it after each request.
This is the default behaviour in uWSGI<=2.0.x

``holy``: creates and destroys the environ dictionary at each request. This is the default behaviour in uWSGI>=2.1
