.. _playhouse:

Playhouse, a collection of addons
=================================

Peewee comes with numerous extras which I didn't really feel like including in
the main source module, but which might be interesting to implementers or fun
to mess around with.


.. _apsw:

apsw, an advanced sqlite driver
-------------------------------

The ``apsw_ext`` module contains a database class suitable for use with
the apsw sqlite driver.

APSW Project page: https://code.google.com/p/apsw/

APSW is a really neat library that provides a thin wrapper on top of SQLite's
C interface, making it possible to use all of SQLite's advanced features.

Here are just a few reasons to use APSW, taken from the documentation:

* APSW gives all functionality of SQLite, including virtual tables, virtual
  file system, blob i/o, backups and file control.
* Connections can be shared across threads without any additional locking.
* Transactions are managed explicitly by your code.
* APSW can handle nested transactions.
* Unicode is handled correctly.
* APSW is faster.

For more information on the differences between apsw and pysqlite,
check `the apsw docs <http://apidoc.apsw.googlecode.com/hg/pysqlite.html>`_.

How to use the APSWDatabase
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from apsw_ext import *

    db = APSWDatabase(':memory:')

    class BaseModel(Model):
        class Meta:
            database = db

    class SomeModel(BaseModel):
        col1 = CharField()
        col2 = DateTimeField()


apsw_ext API notes
^^^^^^^^^^^^^^^^^^

.. py:class:: APSWDatabase(database, **connect_kwargs)

    :param string database: filename of sqlite database
    :param connect_kwargs: keyword arguments passed to apsw when opening a connection

    .. py:method:: transaction([lock_type='deferred'])

        Functions just like the :py:meth:`Database.transaction` context manager,
        but accepts an additional parameter specifying the type of lock to use.

        :param string lock_type: type of lock to use when opening a new transaction

    .. py:method:: register_module(mod_name, mod_inst)

        Provides a way of globally registering a module.  For more information,
        see the `documentation on virtual tables <http://apidoc.apsw.googlecode.com/hg/vtable.html>`_.

        :param string mod_name: name to use for module
        :param object mod_inst: an object implementing the `Virtual Table <http://apidoc.apsw.googlecode.com/hg/vtable.html?highlight=virtual%20table#apsw.VTTable>`_ interface

    .. py:method:: unregister_module(mod_name)

        Unregister a module.

        :param string mod_name: name to use for module

.. note::
    Be sure to use the ``Field`` subclasses defined in the ``apsw_ext``
    module, as they will properly handle adapting the data types for storage.


Sqlite Extensions
-----------------

The SQLite extensions module provides support for some interesting sqlite-only
features:

* Define custom aggregates, collations and functions.
* Basic support for virtual tables.
* Basic support for FTS3/4 (sqlite full-text search).
* Specify isolation level in transactions.


sqlite_ext API notes
^^^^^^^^^^^^^^^^^^^^

.. py:class:: SqliteExtDatabase(database, **kwargs)

    Subclass of the :py:class:`SqliteDatabase` that provides some advanced
    features only offered by Sqlite.

    * Register custom aggregates, collations and functions
    * Specify a row factory
    * Advanced transactions (specify isolation level)

    .. py:method:: aggregate(num_params[, name])

        Class-decorator for registering custom aggregation functions.

        :param num_params: integer representing number of parameters the
            aggregate function accepts.
        :param name: string name for the aggregate, defaults to the name of
            the class.

        .. code-block:: python

            @db.aggregate(1, 'product')
            class Product(object):
                """Like sum, except calculate the product of a series of numbers."""
                def __init__(self):
                    self.product = 1

                def step(self, value):
                    self.product *= value

                def finalize(self):
                    return self.product

            # To use this aggregate:
            product = (Score
                       .select(fn.product(Score.value))
                       .scalar())

    .. py:method:: collation([name])

        Function decorator for registering a custom collation.

        :param name: string name to use for this collation.

        .. code-block:: python

            @db.collation()
            def collate_reverse(s1, s2):
                return -cmp(s1, s2)

            # To use this collation:
            Book.select().order_by(collate_reverse.collation(Book.title))

        As you might have noticed, the original ``collate_reverse`` function
        has a special attribute called ``collation`` attached to it.  This extra
        attribute provides a shorthand way to generate the SQL necessary to use
        our custom collation.

    .. py:method:: func([name[, num_params]])

        Function decorator for registering user-defined functions.

        :param name: name to use for this function.
        :param num_params: number of parameters this function accepts.  If not
            provided, peewee will introspect the function for you.

        .. code-block:: python

            @db.func()
            def title_case(s):
                return s.title()

            # Use in the select clause...
            titled_books = Book.select(fn.title_case(Book.title))

            @db.func()
            def sha1(s):
                return hashlib.sha1(s).hexdigest()

            # Use in the where clause...
            user = User.select().where(
                (User.username == username) &
                (fn.sha1(User.password) == password_hash)).get()

    .. py:method:: granular_transaction([lock_type='deferred'])

        With the ``granular_transaction`` helper, you can specify the isolation level
        for an individual transaction.  The valid options are:

        * ``exclusive``
        * ``immediate``
        * ``deferred``

        Example usage:

        .. code-block:: python

            with db.granular_transaction('exclusive'):
                # no other readers or writers!
                (Account
                 .update(Account.balance=Account.balance - 100)
                 .where(Account.id == from_acct)
                 .execute())

                (Account
                 .update(Account.balance=Account.balance + 100)
                 .where(Account.id == to_acct)
                 .execute())


.. py:class:: VirtualModel

    Subclass of :py:class:`Model` that signifies the model operates using a
    virtual table provided by a sqlite extension.

    .. py:attribute:: _extension = 'name of sqlite extension'


.. py:class:: FTSModel

    Model class that provides support for Sqlite's full-text search extension.
    Models should be defined normally, however there are a couple caveats:

    * Indexes are ignored completely
    * Sqlite will treat all column types as :py:class:`TextField` (although you
      can store other data types, Sqlite will treat them as text).

    Therefore it usually makes sense to index the content you intend to search
    and a single link back to the original document, since all SQL queries
    *except* full-text searches and ``rowid`` lookups will be slow.

    Example:

    .. code-block:: python

        class Document(FTSModel):
            title = TextField()  # type affinities are ignored by FTS, so use TextField
            content = TextField()

        Document.create_table(tokenize='porter')  # use the porter stemmer.

        # populate documents using normal operations.
        for doc in list_of_docs_to_index:
            Document.create(title=doc['title'], content=doc['content'])

        # use the "match" operation for FTS queries.
        matching_docs = Document.select().where(match(Document.title, 'some query'))

        # to sort by best match, use the custom "rank" function.
        best = (Document
                .select(Document, Document.rank('score'))
                .where(match(Document.title, 'some query'))
                .order_by(R('score').desc()))

        # or use the shortcut method:
        best = Document.match('some phrase')

    If you have an existing table and would like to add search for a column
    on that table, you can specify it using the ``content`` option:

    .. code-block:: python

        class Blog(Model):
            title = CharField()
            pub_date = DateTimeField()
            content = TextField()  # we want to search this.

        class FTSBlog(FTSModel):
            content = TextField()

        Blog.create_table()
        FTSBlog.create_table(content=Blog.content)

        # Now, we can manage content in the FTSBlog.  To populate it with
        # content:
        FTSBlog.rebuild()

        # Optimize the index.
        FTSBlog.optimize()

    The ``content`` option accepts either a single :py:class:`Field` or a :py:class:`Model`
    and can reduce the amount of storage used.  However, content will need to be
    manually moved to/from the associated ``FTSModel``.

    .. py:classmethod:: create_table([fail_silently=False[, **options]])

        :param boolean fail_silently: do not re-create if table already exists.
        :param options: options passed along when creating the table, e.g. ``content``.

    .. py:classmethod:: rebuild()

        Rebuild the search index -- this only works when the ``content`` option
        was specified during table creation.

    .. py:classmethod:: optimize()

        Optimize the search index.

    .. py:classmethod:: match(search_phrase)

        Shorthand way of performing a search for a given phrase.  Example:

        .. code-block:: python

            for doc in Document.match('search phrase'):
                print 'match: ', doc.title

    .. py:classmethod:: rank([alias])

        Shorthand way of sorting search results by the quality of their match.

        .. code-block:: python

            docs = (Document
                    .select(Document, Document.rank().alias('score'))
                    .where(match(Document, search))
                    .order_by(R('score').desc()))

        The above code is exactly what the :py:meth:`match` function
        provides.


Postgresql Extension (HStore)
-----------------------------

The postgresql extensions module provides a number of "postgres-only" functions,
currently:

* :ref:`hstore support <hstore>`
* `UUID` field type
* `DateTimeTZ` field type (timezone-aware datetime field)

In the future I would like to add support for more of postgresql's features.
If there is a particular feature you would like to see added, please
`open a Github issue <https://github.com/coleifer/peewee/issues>`_.

.. warning:: In order to start using the features described below, you will need to use the
    extension :py:class:`PostgresqlExtDatabase` class instead of :py:class:`PostgresqlDatabase`.

The code below will assume you are using the following database and base model:

.. code-block:: python

    from playhouse.postgres_ext import *

    ext_db = PostgresqlExtDatabase('peewee_test', user='postgres')

    class BaseExtModel(Model):
        class Meta:
            database = ext_db

.. _hstore:

hstore support
^^^^^^^^^^^^^^

`Postgresql hstore <http://www.postgresql.org/docs/current/static/hstore.html>`_ is
an embedded key/value store.  With hstore, you can store arbitrary key/value pairs
in your database alongside structured relational data.

Currently the ``postgres_ext`` module supports the following operations:

* Store and retrieve arbitrary dictionaries
* Filter by key(s) or partial dictionary
* Update/add one or more keys to an existing dictionary
* Delete one or more keys from an existing dictionary
* Select keys, values, or zip keys and values
* Retrieve a slice of keys/values
* Test for the existence of a key
* Test that a key has a non-NULL value


Using hstore
^^^^^^^^^^^^

To start with, you will need to import the custom database class and the hstore
functions from ``playhouse.postgres_ext`` (see above code snippet).  Then, it is
as simple as adding a :py:class:`HStoreField` to your model:

.. code-block:: python

    class House(BaseExtModel):
        address = CharField()
        features = HStoreField()


You can now store arbitrary key/value pairs on ``House`` instances:

.. code-block:: pycon

    >>> h = House.create(address='123 Main St', features={'garage': '2 cars', 'bath': '2 bath'})
    >>> h_from_db = House.get(House.id == h.id)
    >>> h_from_db.features
    {'bath': '2 bath', 'garage': '2 cars'}


You can filter by keys or partial dictionary:

.. code-block:: pycon

    >>> f = House.features
    >>> House.select().where(f.contains('garage')) # <-- all houses w/garage key
    >>> House.select().where(f.contains(['garage', 'bath'])) # <-- all houses w/garage & bath
    >>> House.select().where(f.contains({'garage': '2 cars'})) # <-- houses w/2-car garage

Suppose you want to do an atomic update to the house:

.. code-block:: pycon

    >>> f = House.features
    >>> new_features = House.features.update({'bath': '2.5 bath', 'sqft': '1100'})
    >>> query = House.update(features=new_features)
    >>> query.where(House.id == h.id).execute()
    1
    >>> h = House.get(House.id == h.id)
    >>> h.features
    {'bath': '2.5 bath', 'garage': '2 cars', 'sqft': '1100'}


Or, alternatively an atomic delete:

.. code-block:: pycon

    >>> query = House.update(features=f.delete('bath'))
    >>> query.where(House.id == h.id).execute()
    1
    >>> h = House.get(House.id == h.id)
    >>> h.features
    {'garage': '2 cars', 'sqft': '1100'}


Multiple keys can be deleted at the same time:

.. code-block:: pycon

    >>> query = House.update(features=f.delete('garage', 'sqft'))

You can select just keys, just values, or zip the two:

.. code-block:: pycon

    >>> f = House.features
    >>> for h in House.select(House.address, f.keys().alias('keys')):
    ...     print h.address, h.keys

    123 Main St [u'bath', u'garage']

    >>> for h in House.select(House.address, f.values().alias('vals')):
    ...     print h.address, h.vals

    123 Main St [u'2 bath', u'2 cars']

    >>> for h in House.select(House.address, f.items().alias('mtx')):
    ...     print h.address, h.mtx

    123 Main St [[u'bath', u'2 bath'], [u'garage', u'2 cars']]

You can retrieve a slice of data, for example, all the garage data:

.. code-block:: pycon

    >>> f = House.features
    >>> for h in House.select(House.address, f.slice('garage').alias('garage_data')):
    ...     print h.address, h.garage_data

    123 Main St {'garage': '2 cars'}

You can check for the existence of a key and filter rows accordingly:

.. code-block:: pycon

    >>> for h in House.select(House.address, f.exists('garage').alias('has_garage')):
    ...     print h.address, h.has_garage

    123 Main St True

    >>> for h in House.select().where(f.exists('garage')):
    ...     print h.address, h.features['garage'] # <-- just houses w/garage data

    123 Main St 2 cars


.. _pwiz:

pwiz, a model generator
-----------------------

``pwiz`` is a little script that ships with peewee and is capable of introspecting
an existing database and generating model code suitable for interacting with the
underlying data.  If you have a database already, pwiz can give you a nice boost
by generating skeleton code with correct column affinities and foreign keys.

If you install peewee using ``setup.py install``, pwiz will be installed as a "script"
and you can just run:

.. highlight:: console
.. code-block:: console

    pwiz.py -e postgresql -u postgres my_postgres_db

This will print a bunch of models to standard output.  So you can do this:

.. code-block:: console

    pwiz.py -e postgresql my_postgres_db > mymodels.py
    python # <-- fire up an interactive shell


.. highlight:: pycon
.. code-block:: pycon

    >>> from mymodels import Blog, Entry, Tag, Whatever
    >>> print [blog.name for blog in Blog.select()]


======    ========================= ============================================
Option    Meaning                   Example
======    ========================= ============================================
-h        show help
-e        database backend          -e mysql
-H        host to connect to        -H remote.db.server
-p        port to connect on        -p 9001
-u        database user             -u postgres
-P        database password         -P secret
-s        postgres schema           -s public
======    ========================= ============================================

The following are valid parameters for the engine:

* sqlite
* mysql
* postgresql


Signal support
--------------

Models with hooks for signals (a-la django) are provided in ``playhouse.signals``.
To use the signals, you will need all of your project's models to be a subclass
of ``playhouse.signals.Model``, which overrides the necessary methods to provide
support for the various signals.

.. highlight:: python
.. code-block:: python

    from playhouse.signals import Model, post_save


    class MyModel(Model):
        data = IntegerField()

    @post_save(sender=MyModel)
    def on_save_handler(model_class, instance, created):
        put_data_in_cache(instance.data)


The following signals are provided:

``pre_save``
    Called immediately before an object is saved to the database.  Provides an
    additional keyword argument ``created``, indicating whether the model is being
    saved for the first time or updated.
``post_save``
    Called immediately after an object is saved to the database.  Provides an
    additional keyword argument ``created``, indicating whether the model is being
    saved for the first time or updated.
``pre_delete``
    Called immediately before an object is deleted from the database when :py:meth:`Model.delete_instance`
    is used.
``post_delete``
    Called immediately after an object is deleted from the database when :py:meth:`Model.delete_instance`
    is used.
``pre_init``
    Called when a model class is first instantiated
``post_init``
    Called after a model class has been instantiated and the fields have been populated,
    for example when being selected as part of a database query.


Connecting handlers
^^^^^^^^^^^^^^^^^^^

Whenever a signal is dispatched, it will call any handlers that have been registered.
This allows totally separate code to respond to events like model save and delete.

The :py:class:`Signal` class provides a :py:meth:`~Signal.connect` method, which takes
a callback function and two optional parameters for "sender" and "name".  If specified,
the "sender" parameter should be a single model class and allows your callback to only
receive signals from that one model class.  The "name" parameter is used as a convenient alias
in the event you wish to unregister your signal handler.

Example usage:

.. code-block:: python

    from playhouse.signals import *

    def post_save_handler(sender, instance, created):
        print '%s was just saved' % instance

    # our handler will only be called when we save instances of SomeModel
    post_save.connect(post_save_handler, sender=SomeModel)

All signal handlers accept as their first two arguments ``sender`` and ``instance``,
where ``sender`` is the model class and ``instance`` is the actual model being acted
upon.

If you'd like, you can also use a decorator to connect signal handlers.  This is
functionally equivalent to the above example:

.. code-block:: python

    @post_save(sender=SomeModel)
    def post_save_handler(sender, instance, created):
        print '%s was just saved' % instance


Signal API
^^^^^^^^^^

.. py:class:: Signal()

    Stores a list of receivers (callbacks) and calls them when the "send" method is invoked.

    .. py:method:: connect(receiver[, sender=None[, name=None]])

        Add the receiver to the internal list of receivers, which will be called
        whenever the signal is sent.

        :param callable receiver: a callable that takes at least two parameters,
            a "sender", which is the Model subclass that triggered the signal, and
            an "instance", which is the actual model instance.
        :param Model sender: if specified, only instances of this model class will
            trigger the receiver callback.
        :param string name: a short alias

        .. code-block:: python

            from playhouse.signals import post_save
            from project.handlers import cache_buster

            post_save.connect(cache_buster, name='project.cache_buster')

    .. py:method:: disconnect([receiver=None[, name=None]])

        Disconnect the given receiver (or the receiver with the given name alias)
        so that it no longer is called.  Either the receiver or the name must be
        provided.

        :param callable receiver: the callback to disconnect
        :param string name: a short alias

        .. code-block:: python

            post_save.disconnect(name='project.cache_buster')

    .. py:method:: send(instance, *args, **kwargs)

        Iterates over the receivers and will call them in the order in which
        they were connected.  If the receiver specified a sender, it will only
        be called if the instance is an instance of the sender.

        :param instance: a model instance


    .. py:method __call__([sender=None[, name=None]])

        Function decorator that is an alias for a signal's connect method:

        .. code-block:: python

            from playhouse.signals import connect, post_save

            @post_save(name='project.cache_buster')
            def cache_bust_handler(sender, instance, *args, **kwargs):
                # bust the cache for this instance
                cache.delete(cache_key_for(instance))


Generic foreign keys
--------------------

The ``gfk`` module provides a Generic ForeignKey (GFK), similar to Django.  A GFK
is composed of two columns: an object ID and an object type identifier.  The
object types are collected in a global registry (``all_models``).

How a :py:class:`GFKField` is resolved:

1. Look up the object type in the global registry (returns a model class)
2. Look up the model instance by object ID

.. note:: In order to use Generic ForeignKeys, your application's models *must*
    subclass ``playhouse.gfk.Model``.  This ensures that the model class will
    be added to the global registry.

.. note:: GFKs themselves are not actually a field and will not add a column
    to your table.

Like regular ForeignKeys, GFKs support a "back-reference" via the :py:class:`ReverseGFK`
descriptor.

How to use GFKs
^^^^^^^^^^^^^^^

1. Be sure your model subclasses ``playhouse.gfk.Model``
2. Add a :py:class:`CharField` to store the ``object_type``
3. Add a field to store the ``object_id`` (usually a :py:class:`IntegerField`)
4. Add a :py:class:`GFKField` and instantiate it with the names of the ``object_type``
   and ``object_id`` fields.
5. (optional) On any other models, add a :py:class:`ReverseGFK` descriptor

Example:

.. code-block:: python

    from playhouse.gfk import *

    class Tag(Model):
        tag = CharField()
        object_type = CharField(null=True)
        object_id = IntegerField(null=True)
        object = GFKField('object_type', 'object_id')

    class Blog(Model):
        tags = ReverseGFK(Tag, 'object_type', 'object_id')

    class Photo(Model):
        tags = ReverseGFK(Tag, 'object_type', 'object_id')

How you use these is pretty straightforward hopefully:

.. code-block:: pycon

    >>> b = Blog.create(name='awesome post')
    >>> Tag.create(tag='awesome', object=b)
    >>> b2 = Blog.create(name='whiny post')
    >>> Tag.create(tag='whiny', object=b2)

    >>> b.tags # <-- a select query
    <class '__main__.Tag'> SELECT t1."id", t1."tag", t1."object_type", t1."object_id" FROM "tag" AS t1 WHERE ((t1."object_type" = ?) AND (t1."object_id" = ?)) [u'blog', 1]

    >>> [x.tag for x in b.tags]
    [u'awesome']

    >>> [x.tag for x in b2.tags]
    [u'whiny']

    >>> p = Photo.create(name='picture of cat')
    >>> Tag.create(object=p, tag='kitties')
    >>> Tag.create(object=p, tag='cats')

    >>> [x.tag for x in p.tags]
    [u'kitties', u'cats']

    >>> [x.tag for x in Blog.tags]
    [u'awesome', u'whiny']

    >>> t = Tag.get(Tag.tag == 'awesome')
    >>> t.object
    <__main__.Blog at 0x268f450>

    >>> t.object.name
    u'awesome post'

GFK API
^^^^^^^

.. py:class:: GFKField([model_type_field='object_type'[, model_id_field='object_id']])

    Provide a clean API for storing "generic" foreign keys.  Generic foreign keys
    are comprised of an object type, which maps to a model class, and an object id,
    which maps to the primary key of the related model class.

    Setting the GFKField on a model will automatically populate the ``model_type_field``
    and ``model_id_field``.  Similarly, getting the GFKField on a model instance
    will "resolve" the two fields, first looking up the model class, then looking
    up the instance by ID.

.. py:class:: ReverseGFK(model, [model_type_field='object_type'[, model_id_field='object_id']])

    Back-reference support for :py:class:`GFKField`.


Key/Value Store
---------------

Provides a simple key/value store, using a dictionary API.  By default the
the :py:class:`KeyStore` will use an in-memory sqlite database, but any database
will work.

To start using the key-store, create an instance and pass it a field to use
for the values.

.. code-block:: python

    >>> kv = KeyStore(TextField())
    >>> kv['a'] = 'A'
    >>> kv['a']
    'A'

.. note::
  To store arbitrary python objects, use the :py:class:`PickledKeyStore`, which
  stores values in a pickled :py:class:`BlobField`.

Using the :py:class:`KeyStore` it is possible to use "expressions" to retrieve
values from the dictionary.  For instance, imagine you want to get all keys
which contain a certain substring:

.. code-block:: python

    >>> keys_matching_substr = kv[kv.key % '%substr%']
    >>> keys_start_with_a = kv[fn.Lower(fn.Substr(kv.key, 1, 1)) == 'a']

KeyStore API
^^^^^^^^^^^^

.. py:class:: KeyStore(value_field[, ordered=False[, database=None]])

    Lightweight dictionary interface to a model containing a key and value.
    Implements common dictionary methods, such as ``__getitem__``, ``__setitem__``,
    ``get``, ``pop``, ``items``, ``keys``, and ``values``.

    :param Field value_field: Field instance to use as value field, e.g. an
        instance of :py:class:`TextField`.
    :param boolean ordered: Whether the keys should be returned in sorted order
    :param Database database: :py:class:`Database` class to use for the storage
        backend.  If none is supplied, an in-memory Sqlite DB will be used.

    Example:

    .. code-block:: pycon

        >>> from playhouse.kv import KeyStore
        >>> kv = KeyStore(TextField())
        >>> kv['a'] = 'foo'
        >>> for k, v in kv:
        ...     print k, v
        a foo

        >>> 'a' in kv
        True
        >>> 'b' in kv
        False

.. py:class:: PickledKeyStore([ordered=False[, database=None]])

    Identical to the :py:class:`KeyStore` except *anything* can be stored as
    a value in the dictionary.  The storage for the value will be a pickled
    :py:class:`BlobField`.

    Example:

    .. code-block:: pycon

        >>> from playhouse.kv import PickledKeyStore
        >>> pkv = PickledKeyStore()
        >>> pkv['a'] = 'A'
        >>> pkv['b'] = 1.0
        >>> list(pkv.items())
        [(u'a', 'A'), (u'b', 1.0)]


.. _proxy:

Proxy
-----

Proxy class useful for situations when you wish to defer the initialization of
an object.  For instance, you want to define your models but you do not know
what database engine you will be using until runtime.

.. code-block:: python

    database_proxy = Proxy()  # Create a proxy for our db.

    class BaseModel(Model):
        class Meta:
            database = database_proxy  # Use proxy for our DB.

    class User(BaseModel):
        username = CharField()

    # Based on configuration, use a different database.
    if app.config['DEBUG']:
        database = SqliteDatabase('local.db')
    elif app.config['TESTING']:
        database = SqliteDatabase(':memory:')
    else:
        database = PostgresqlDatabase('mega_production_db')

    # Configure our proxy to use the db we specified in config.
    database_proxy.initialize(database)


Proxy API
^^^^^^^^^

.. py:class:: Proxy()

    Create a new :py:class:`Proxy` instance.

    .. py:method:: initialize(obj)

        :param obj: The object to proxy to.

        Once initialized, the attributes and methods on ``obj`` can be accessed
        directly via the :py:class:`Proxy` instance.


Test Utils
----------

Contains utilities helpful when testing peewee projects.

.. py:class:: test_database(db, models[, create_tables=True[, fail_silently=False]])

    Context manager that lets you use a different database with a set of
    models.  Models can also be automatically created and dropped.

    This context manager helps make it possible to test your peewee models
    using a "test-only" database.

    :param Database db: Database to use with the given models
    :param models: a ``list`` of :py:class:`Model` classes to use with the ``db``
    :param boolean create_tables: Whether tables should be automatically created
        and dropped.
    :param boolean fail_silently: Whether the table create / drop should fail
        silently.

    Example:

    .. code-block:: python

        from unittest import TestCase
        from playhouse.test_utils import test_database
        from peewee import *

        from my_app.models import User, Tweet

        test_db = SqliteDatabase(':memory:')

        class TestUsersTweets(TestCase):
            def create_test_data(self):
                # ... create a bunch of users and tweets
                for i in range(10):
                    User.create(username='user-%d' % i)

            def test_timeline(self):
                with test_database(test_db, (User, Tweet)):
                    # This data will be created in `test_db`
                    self.create_test_data()

                    # Perform assertions on test data inside ctx manager.
                    self.assertEqual(Tweet.timeline('user-0') [...])

                # once we exit the context manager, we're back to using the normal database
