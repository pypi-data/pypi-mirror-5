=================
Django Principals
=================

This module provides ``PrincipalField``, a model field for Django_ that allows
instances of a model to be defined as the principal instance for an entire model or
a collection of instances. When the status of one instance is changed, the status
of other items in the collection are updated in response as necessary.


Usage
-----

Add a ``PrincipalField`` to your model; that's it.

If you want to work with all instances of the model as a single collection,
there's nothing else required.  To create collections based on one or more
fields on the model, specify the field names using the ``collection`` argument.

In general, the value assigned to a ``PrincipalField`` will be handled like a
unique Boolean value.  Setting the principal to ``True`` will
cause all other items to become ``False``within the same collection --
unless, of course, the collection has fewer than two elements.

Multi-table model inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, if a parent model has a principal field that declares a collection,
child model instances are filtered independently. This behavior can be changed
by specifying a `parent_link` argument identifying the name of the one-to-one
field linking the child model to the parent. If `parent_link` is set, all subclass
instances will be part of a single sequence in each collection.


Limitations
-----------

* Unique constraints can't be applied to ``PrincipalField`` because they break
  the ability to update other items in a collection all at once.  This one was
  a bit painful, because setting the constraint is probably the right thing to
  do from a database consistency perspective, but the overhead in additional
  queries was too much to bear.

Credits
-------

This code loosely draws on concepts inspired by django-positions_ and django-featured-item_,
two projects which provide custom model fields with different functionality.


.. _`Django`: http://www.djangoproject.com/

.. _`django-positions`: https://github.com/jpwatts/django-positions

.. _`django-featured-item`:  https://bitbucket.org/tim_heap/django-featured-item
