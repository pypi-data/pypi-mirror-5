Caching PyPI Proxy
==================

Use proxypypi to set up a transparent caching proxy to PyPI
(https://pypy.python.org/) to:

1. make your installs res/ilient against Internet/PyPI issues,
2. speed up your installs significantly (after the first one),
3. prevent problems installing packages that are removed from distribution by
   the author,
4. allow installation of packages from within a firewalled environment where
   the host performing the installation does not have Internet access, and
5. allow hosting and installation of private packages.

When the proxy is asked about a package it doesn't know it automatically goes
off and fetches the file download list for the package, rewriting all
references (PyPI and external) so they appear to be local. On request of one
of those now-local package file references it performs a background fetch of
the file contents and serves up the new file data to the pip request (thus
keeping that request alive despite its very short timeout duration).


Why Another One?
----------------

There's a lot of PyPI-alike implementations and "proxy" servers out there.
This proxy differs from almost all others (save devpi-server) in that it
automatically relocates package download files from the Internet to your local
server. It differs from devpi-server in that it has no external database
requirement (just a filesystem is needed) making deployment much simpler (at
least for me).


Usage
-----

Setup of proxypypi requires:

1. "pip install proxypypi"
2. cd to some directory you would like files to be cached in
3. proxypypi run

There are some command-line arguments (see "proxypypi -h") that allow some
run-time behaviour control. Notably "-d" which can configure the directory
to cache in.

Additionally the proxy may run in the background, in which case you need to
supply three additional command-line arguments: "-P" (PID file), "-l" (log
file) and "-o" (console output file) and use one of the daemon control commands
instead of "run". See "proxypypi -h" for the commands.

Once running you may perform pip installs using the proxy by including the
proxy in the pip command line using the "-i" argument:

   pip install -i http://proxy_host:proxy_port/simple/ package_to_install

Any packages not cached will be fetched into the cache and the install will
continue as normal.


Private (or Manually Downloaded) Packages
-----------------------------------------

Package distribution files added to the root of the package directory served
by proxypypi will be served alongside those it proxies requests for. You may,
if you wish, make package-named subdirectories, but it's not necessary.


Upgrading Cached Packages
-------------------------

This isn't done yet :-)


Version History
---------------

- 1.0 first public releae
- 1.0.1 clear up handling of paths to daemon files
- 1.2 handle external files that don't exist (issue 1, thanks George Hickman)
- 1.2.1 fix a name collision issue
