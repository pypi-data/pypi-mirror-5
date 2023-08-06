staticserve
=============

This distribution provides an easy way to include static content
in your WSGI applications. There is a convenience method for serving
files located via pkg_resources. There are also facilities for serving
mixed (static and dynamic) content using "magic" file handlers.
Python builtin string substitution is provided and it is easy to roll
your own handlers. Also provides a command of the same name as a convenience
when you just want to share a little content over HTTP, ad hoc.

**Note**: A Python 2.7/3.3 compatible fork of Luke Arno's static package.