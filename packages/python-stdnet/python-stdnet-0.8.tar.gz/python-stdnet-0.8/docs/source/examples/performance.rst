.. _increase-performance:

.. module:: stdnet.odm

======================
Performance
======================

We dig deeper into our example by exploring additional features of
the API, including the manipulation of related models and transactions.


.. _model-transactions:

Transactions
========================

Under the hood, stdnet performs server updates and queries
via a :class:`Session`. You can write your application without
using a session directly, and in several cases this is good enough.
However, when dealing with lots of operations, you may be better off
using :class:`Transaction`. A transaction is started
with the :meth:`Session.begin` method and concluded with
the :meth:`Session.commit` method. A session for
:ref:`registered models <register-model>` can be obtained from the model
manager. For example, using the ``Fund`` model in
:ref:`tutorial 1 <tutorial-application>`::

    session = Fund.objects.session()
    session.begin() # start a new transaction
    session.add(Fund(name='Markowitz', ccy='EUR'))
    session.add(Fund(name='SterlingFund', ccy='GBP'))
    session.commit() # commit changes to the server


Transactions are pivotal for two reasons:

* They guarantee atomicity and therefore consistency of model instances when updating/deleting.
* They speed up updating, deleting and retrieval of several independent block
  of data at once.

For certain type of operations, the use of transactions becomes almost compulsory
as the speed up achived can be of 2 to 3 order of magnitude.

This snippet demonstrates how to speed up the creation of several instances of
model ``Fund`` using a ``with`` statement::

    with Fund.objects.transaction() as t:
        for kwargs in data:
            t.add(Fund(**kwargs))

Or for more than one model::


    with Fund.objects.transaction(Instrument) as t:
        for kwargs in data1:
            t.add(Fund(**kwargs))
        for kwargs in data2:
            t.add(Instrument(**kwargs))
        ...


As soon as the ``with`` statement finishes, the transaction commit changes
to the server via the :meth:`commit` method.


.. _performance-loadonly:

Use load_only
================

One of the main advantages of using key-values databases as opposed to
traditional relational databases, is the ability to add or remove
:class:`Field` without requiring database migration.
In addition, the :class:`JSONField` can be a factory
of fields for a given model (when used with the :attr:`JSONField.as_string`
set to ``False``).
For complex models, :class:`Field` can also be used as cache.

In these situations, your model may contain a lot of fields, some of which
could contain a lot of data (for example, text fields), or require
expensive processing to convert them to Python objects.
If you are using the results of a :class:`Query` in a situation
where you know you don't need those particular fields, you can tell stdnet
to load a subset of fields from the database by using the :meth:`Query.load_only`
or :meth:`Query.dont_load` methods.

For example I need to load all my *EUR* Funds from the
:ref:`example application <tutorial-application>`
but I don't need to see the *description* and *ccy*::

    qs = Fund.objects.filter(ccy="EUR").load_only('name')

Importantly, the ``load_only`` method can also be applied to :ref:`related objects
<tutorial-related>` fields. For example if I need to load ``Positions`` from
:ref:`example application <tutorial-application>` and only the currency field
is required from the ``instrument`` field one could issue the command::

    qs = Position.objects.query().load_only('instrument__ccy')

This is equivalent to the use of :meth:`Query.load_related`::

    qs = Position.objects.query().load_related('instrument', 'ccy')


Use dont_load
================

Opposite of :ref:`load_only <performance-loadonly>`, it can be used to avoid
loading a subsets of fields::

    qs = Fund.objects.filter(ccy="EUR").dont_load('description', 'ccy')



.. _performance-loadrelated:

Use load_related
====================
The :meth:`Query.load_related` method is another performance boost tool when
used in the right circumstances. It is similar to the `eager loading`_ in SqlAlchemy
and the `select_related`_ in Django.
The method returns a new :meth:`Query` that automatically load the
:class:`ForeignKey` field at the same time as the parent object, within a single
back-end roundtrip.

This is a performance booster which results in (sometimes much) larger queries
but means later use of foreign-key relationships won't require database queries.

Let's consider the :ref:`Position model <tutorial-application>` in the
tutorial application and lets assume we need to access the ``instrument`` and ``fund``
foreign keys::


    positions = Position.objects.query()
    for p in positions:
        # requires one database roundtrip
        i = p.instrument
        # requires another database roundtrip
        f = p.fund
        
Since foreign key are not loaded by default, when accessing the field for the first time,
stdnet needs to load it from the backend-server. Check
:ref:`one to many relationship <one-to-many>` tutorial for more information on
lazy loading.

The above example can be drammatically speeded up by modifying the query in
the following way::

    positions = Position.objects.query().load_related('instrument')\
                                        .load_related('fund')
    for p in positions:
        # No database roundtrip
        i = p.instrument
        # No database roundtrip
        f = p.fund
        

Get single fields
====================
It is possible to obtain only the values of a given field. If
I need to obtain all the Funds names from the :ref:`example application <tutorial-application>`
I could issue the following command::

    names = Fund.objects.query().get_field('name')

The :meth:`Q.get_field` method returns a new query which evaluates to a
list of field values.


.. _`eager loading`: http://docs.sqlalchemy.org/en/latest/orm/loading.html
.. _`select_related`: https://docs.djangoproject.com/en/dev/ref/models/querysets/#select-related