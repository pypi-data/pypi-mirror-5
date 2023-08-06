================
pygments-asl
================

.. image:: https://api.travis-ci.org/curzona/pygments-asl.png
   :target: https://travis-ci.org/curzona/pygments-asl
   
------------------------------------------------
A Pygments lexer for ACPI source language (ASL)
------------------------------------------------

Overview
========

This package provides an ACPI_ source language (ASL) lexer for Pygments_.
The lexer is published as an entry point and, once installed, Pygments will
pick it up automatically.

You can then use the ``asl`` language with Pygments::

    $ pygmentize -l asl test.asl

.. _ACPI: http://www.acpi.info/
.. _Pygments: http://pygments.org/

Installation
============

Use your favorite installer to install pygments-asl into the same
Python you have installed Pygments. For example::

    $ easy_install pygments-asl

To verify the installation run::

    $ pygmentize -L lexer | grep -i asl
    * asl:
        ASL (filenames *.asl, *.aml)

