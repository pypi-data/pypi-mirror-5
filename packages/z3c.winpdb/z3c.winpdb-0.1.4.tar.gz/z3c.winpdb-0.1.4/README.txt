.. contents::

Introduction
============
z3c.winpdb is a trivial package that calls rpbd2.start_embedded_debugger
when IDatabaseOpenedWithRootEvent is fired during the startup of the
Zope / Plone instance thus making it possible to debug the running instance
with winpdb.

Two environment variables are evaluated:

RPDB2_ENABLE must be set to "true" for start_embedded_debugger to be called.
You most probably don't want this in a production environment.
Default is "false".

In RPDB2_PASSWD you can set the password needed to attach winpdb to the
embedded debugger.
Default is "passwd".

Note
====
You can't use z3c.winpdb and use python profiling concurrently, as this causes
an infinite recursion in rpdb2's CDebuggerCoreThread.profile_recursion method.
So if you use z3c.winpdb make sure to remove any publisher-profile-file
directive from zope.conf file.
