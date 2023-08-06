==========
PufferFish
==========

Pufferfish provides a FileSystemEntity class that can be used for those mapped
objects that need to keep files on the filesystem (i.e. to be served by the
webserver directly). It uses SQLAlchemy 0.7 events to handle rollback and
commits on deleted/updated and new objects (a new file will be removed on
rollbacks, while a delete file will be removed only after a successful commit,
etc).




