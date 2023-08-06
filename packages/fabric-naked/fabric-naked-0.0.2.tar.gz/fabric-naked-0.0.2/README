Overview
========
あなたの手順書をfabricで簡単に実行できるようにします。

Installation
============

fabric-naked is installed easily.

::

    easy_install fabric-naked

or

::

    pip install fabric-naked

Usage
=====

1. make your working procedure
1. execute it by fabric

::

    $ cat  your_procedure.cmds
    # this is comment
        # this is comment too
    $ hostname
    $ date
    local$ printf "SCHEDULE_HOST_CHECK;%s\n" `hostname`
    sudo$ date
    sudo@yuokda$ date

    $ fab execute_naked_procedure:your_procedure.dsl

Changelog
=========

0.1.0 (2013-07-13)
------------------
- First release


Travis
======

`Travis CI - Distributed build platform for the open source community <http://travis-ci.org/#!/yuokada/python-babigo>`_

.. image :: https://secure.travis-ci.org/yuokada/python-babigo.png?branch=master
