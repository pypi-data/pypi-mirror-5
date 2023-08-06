==========
PufferFish
==========

PufferFish provides an SQLAlchemy session that provides hooks for various
events link commits and rollbacks.
It provides a FileSystemEntity class that can be used as a base Elixir class
for those entities that need to keep files on the filesystem (i.e. to be
served by the webserver directly). It use session hooks to handle rollback and
commits on deleted/updated and new objects ( a new file will be removed on
rollbacks, while a delete file will be removed only after a successful commit,
etc)




