js.namespace
************

Introduction
============

This library provides a small javascript library to declare namespaces,
packaged for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org


Create and use a namespace
==========================

Once included, you can use namespace.declare('your.namespace'); to declare a
namespace. Then you can bind objects to that namespace by just assigning them
like your.namespace.your_funky_function = function(foo) {…};

You are then able to access these objects from anywhere, without polluting the
global scope. Using dotted namespaces is a well known pattern to get a nice
and tidy codebase.

