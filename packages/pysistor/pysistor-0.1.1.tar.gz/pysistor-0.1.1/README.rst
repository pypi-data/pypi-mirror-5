Pysistor
========

Pysistor serves as a thin abstraction layer for persistence mechanisms. It was designed mainly to fill two use cases:

1. You are writing a library, and you'd love for it to work on Pyramid, Flask, Django, etc, but they all store stuff slightly different. This lets you interface with all of them (soon).
2. You want to use differnt backends between testing and production, or dev and testing. Perhaps your dev computers don't want to run memcached, so instead a simple file backend will suffice for storing _____.

**Note**: Project is on it's way, but not feature complete yet...

License
-------

BSD
