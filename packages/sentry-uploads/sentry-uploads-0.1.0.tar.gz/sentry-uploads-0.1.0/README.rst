sentry-uploads
==============

A Sentry extension that adds support for uploading files.

WARNING
-------

Sentry is not designed for this sort of usage: it does not support streaming
data, and uploading large files through this mechanism can easily exhaust
memory and cause a crash, on both the client and server sides.

Use with care, at your own risk!

Install
-------

Install the package via ``pip``::

    pip install sentry-uploads

Usage
-----

To upload files from your client send data for the
``sentry_uploads.interfaces.Uploads`` interface. This data should have one key,
``files``, whose value should be an array of dictionaries containing the
following keys:

* ``filename   The name of the file.``
* ``data       The compressed uuencoded file contents, as returned by the sentry.utils.strings.compress function.``
* ``type       The file's MIME type (optional).``

For an example of how to generate the appropriate data see the example/test
script sentry_uploads/scripts/runner.py in this package.
