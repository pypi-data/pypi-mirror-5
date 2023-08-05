=======
amqpclt
=======

.. image:: https://secure.travis-ci.org/cern-mig/python-amqpclt.png?branch=master

Overview
========

amqpclt is a versatile tool to interact with messaging brokers speaking AMQP
and/or message queues (see messaging.queue) on disk.

It receives messages (see messaging.message) from an incoming module,
optionally massaging them (i.e. filtering and/or modifying), and sends
them to an outgoing module. Depending on which modules are used, the tool
can perform different operations.

Install
=======

To install this module, run the following command::

    python setup.py install

To test the module, run the following command::

    python setup.py test

Support and documentation
=========================

After installing, you can find documentation for this module with the
standard python help function command or at:

    https://amqpclt.readthedocs.org/

License and Copyright
=====================

Copyright (C) 2013 CERN

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0 

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License.
