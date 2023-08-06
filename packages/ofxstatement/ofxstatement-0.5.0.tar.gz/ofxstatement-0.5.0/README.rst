~~~~~~~~~~~~~
OFX Statement
~~~~~~~~~~~~~

.. image:: https://travis-ci.org/kedder/ofxstatement.png?branch=master
    :target: https://travis-ci.org/kedder/ofxstatement
.. image:: https://coveralls.io/repos/kedder/ofxstatement/badge.png?branch=master
    :target: https://coveralls.io/r/kedder/ofxstatement?branch=master

Ofxstatement is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Package provides single command line tool to
run: ``ofxstatement``. Run ``ofxstatement -h`` to see basic usage description.
``ofxstatement`` works under Python 3 and is not compatible with Python 2.


Rationale
=========

Most internet banking systems are capable of exporting account transactions to
some sort of computer readable formats, but few supports standard data formats,
like `OFX`_.  On the other hand, personal accounting tools, such as `GnuCash`_
support standard formats only, and will probably never support proprietary
statement formats of online banking systems.

To bridge the gap between them, ofxstatement tool was created.

.. _GnuCash: http://gnucash.org/
.. _OFX: http://en.wikipedia.org/wiki/Open_Financial_Exchange

Mode of Operation
=================

The ``ofxstatement`` tool is intended to be used in the following workflow:

1. At the end of each month, use your online banking service to export
   statements from all of your bank accounts to files in formats, known to
   ofxstatement.

2. Run ``ofxstatement`` on each exported file to convert it to standard OFX
   format.  Shell scripts or Makefile may help to automate this routine.

3. Import generated OFX files to GnuCash or other accounting system.

Installation and Usage
======================

Before using ``ofxstatement``, you have to install plugin for your bank (or
write your own!). Plugins are installed as regular python eggs, with
easy_install or pip, for example::

  $ pip3 install ofxstatement-lithuanian

Note, that ofxstatement itself will be installed automatically this way. After
installation, ``ofxstatement`` utility should be available. You can check it
is working by running::

  $ ofxstatement list-plugins

You should get a list of your installed plugins printed.

After installation, usage is simple::

  $ ofxstatement convert -t <plugin> bank_statement.csv statement.ofx

Resulting ``statement.ofx`` is then ready to be imported to GnuCash or other
financial program you use.


Known Plugins
=============

There are several user-developed plugins available:

=========================== ==================================================
Plugin                      Description
=========================== ==================================================
`ofxstatement-lithuanian`_  Plugins for several banks, operating in
                            Lithuania: Swedbank, Danske and common Lithuanian
                            exchange format - LITAS-ESIS.

`ofxstatement-czech`_       Plugin for Poštovní spořitelna (``maxibps``)

`ofxstatement-bubbas`_      Set of plugins, developed by @bubbas: ``dkb_cc``
                            and ``lbbamazon``.
=========================== ==================================================

.. _ofxstatement-lithuanian: https://github.com/kedder/ofxstatement-lithuanian
.. _ofxstatement-czech: https://github.com/kedder/ofxstatement-czech
.. _ofxstatement-bubbas: https://github.com/kedder/ofxstatement-bubbas

Advanced Configuration
======================

While ofxstatement can be used without any configuration, some plugins may
accept additional configuration parameters. These parameters can be specified
in configuration file. Configuration file can be edited using ``edit-config``
command, that brings your favored editor with configuration file open::

  $ ofxstatement edit-config

Configuration file format is a standard .ini format. Configuration is divided
to sections, that corresponds to ``--type`` command line parameter. Each
section must provide ``plugin`` option that points to one of the registered
conversion plugins. Other parameters are plugin specific.

Sample configuration file::

    [swedbank]
    plugin = swedbank

    [dabske:usd]
    plugin = litas-esis
    charset = cp1257
    currency = USD
    account = LT123456789012345678


Such configuration will let ofxstatement to know about two statement file
format, handled by plugins ``swedbank`` and ``litas-esis``. ``litas-esis``
plugin will load statements using ``cp1257`` charset and set custom currency
and custom account number. This way, GnuCash will automatically associate
imported .ofx statement with particular GnuCash account.

To convert proprietary ``danske.csv`` to OFX ``danske.ofx``, run::

    $ ofxstatement -t danske:usd danske.csv danske.ofx

Note, that configuration parameters are plugin specific. See particular plugin
documentation for more info.

Writing your own Plugin
=======================

If plugin for your bank is not yet developed (see `Known plugins`_ section
above), you can easily write your own, provided some knowledge about python
programming language. There is an `ofxstatement-sample`_ plugin project
available, that provides sample boilerplate and describes plugin development
process in detail.

.. _ofxstatement-sample: https://github.com/kedder/ofxstatement-sample
