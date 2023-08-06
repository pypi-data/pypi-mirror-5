===================
buildout.disablessl
===================

setuptools-0.7 introduced verification of SSL certificates. This feature,
however, is not configurable (yet?), which makes it impossible to install
packages from a custom package index with a self-signed certificate, for
example.

This package is a very small, monkey-patching buildout extension that simply
sets "ssl avaiable" to false. Use it like so::

    [buildout]
    extensions = buildout.disablessl


WARNING: Using this extension disables SSL verification (duh), so you make
yourself susceptible to man-in-the-middle attacks (among other things). Use
with caution!
