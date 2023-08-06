===========================
 httplib2.ca_certs_locater
===========================

This package provides a plug-in to httplib2 to tell it to use the
certificate authority file from the base OS instead of the one in the
httplib2 package. The file from httplib2 is used as a fallback, if the
expected OS-specific file is not found.

Installation
============
First install `pbr`_ package::

  $ pip install pbr

Then run::

  $ pip install httplib2.ca_certs_locater

Supporting Additional Platforms
===============================

If you are on a platform with a different certificate authority file,
please submit a pull request via `github`_ to add the file to ``get()``.

.. _`github`: https://github.com/dreamhost/httplib2-ca_certs_locater
.. _`pbr`: https://github.com/openstack-dev/pbr
