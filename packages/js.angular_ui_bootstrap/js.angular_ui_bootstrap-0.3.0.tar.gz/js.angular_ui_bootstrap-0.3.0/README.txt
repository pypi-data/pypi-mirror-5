js.angular_ui_bootstrap
***********************

Introduction
============

This library packages `Angular UI Bootstrap`_ for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org
.. _`Angular UI Bootstrap`: http://angular-ui.github.io/bootstrap/

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``js.angular_ui_bootstrap``) are published to some URL.

How to use?
===========

You can import ``angular_ui_bootstrap`` from ``js.angular_ui_bootstrap`` and ``need`` it where you want
these resources to be included on a page::

  >>> from js.angular_ui_bootstrap import angular_ui_bootstrap
  >>> angular_ui_bootstrap.need()

Caveat
======

At the moment, the package only serves the `tpls` version, i.e. shipped with the default templates. From the Angular UI Bootstrap doc:

    Then we've got files with the -tpls. To explain the difference let's start by explaining that we want our directives to be highly customizable. To achieve this we are trying hard not to hard-code markup nor CSS inside JavaScript code. Instead most of the directives are coming with a dedicated template(s) so people can change them. We are providing default templates based on Twitter's markup and CSS but you should be able to prepare your own partials to change the look&feel of widgets from this repo.
    Now it should be clear that files with the -tpls in their name have bootstrap-specific templates bundled with directives. For people who don't want to take all the directives and don't need to customize anything the solution is to grab a file named ui-bootstrap-tpls-[version].min.js.::

