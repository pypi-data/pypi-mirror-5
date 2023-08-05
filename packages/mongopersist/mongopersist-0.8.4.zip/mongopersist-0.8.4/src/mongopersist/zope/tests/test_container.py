##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Mongo Persistence Doc Tests"""
import atexit
import doctest

import ZODB
import ZODB.DemoStorage
import persistent
import pymongo
import random
import re
import transaction
import zope.component
import zope.interface
import zope.lifecycleevent
from pprint import pprint
from zope.exceptions import exceptionformatter
from zope.app.testing import placelesssetup
from zope.container import contained, btree
from zope.testing import cleanup, module, renormalizing

from mongopersist import datamanager, interfaces, serialize, testing
from mongopersist.zope import container

DBNAME = 'mongopersist_container_test'


class ApplicationRoot(container.SimpleMongoContainer):
    _p_mongo_collection = 'root'

    def __repr__(self):
        return '<ApplicationRoot>'


class SimplePerson(contained.Contained, persistent.Persistent):
    _p_mongo_collection = 'person'

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s>' %(self.__class__.__name__, self)


class Person(container.MongoContained, SimplePerson):
    pass


def doctest_MongoContained_simple():
    """MongoContained: simple use

    The simplest way to use MongoContained is to use it without any special
    modification. In this case it is required that the container always sets
    the name and parent after loading the item. It can do so directly by
    setting ``_v_name`` and ``_v_parent`` so that the persistence mechanism
    does not kick in.

      >>> class Simples(container.MongoContainer):
      ...     def __init__(self, name):
      ...         super(Simples, self).__init__()
      ...         self.name = name
      ...     def __repr__(self):
      ...         return '<Simples %s>' %self.name

      >>> class Simple(container.MongoContained, persistent.Persistent):
      ...     pass

    Let's create a simple component and activate the persistence machinery:

      >>> s = Simple()
      >>> s._p_jar = dm

    As you can see, the changed flag is not changed:

      >>> s._p_changed
      False
      >>> s._v_name = 'simple'
      >>> s._v_parent = Simples('one')
      >>> s._p_changed
      False

    And accessing the name and parent works:

      >>> s.__name__
      'simple'
      >>> s.__parent__
      <Simples one>

    But assignment works as well.

      >>> s.__name__ = 'simple2'
      >>> s.__name__
      'simple2'
      >>> s.__parent__ = Simples('two')
      >>> s.__parent__
      <Simples two>
      >>> s._p_changed
      True
    """

def doctest_MongoContained_proxy_attr():
    """MongoContained: proxy attributes

    It is also possible to use proxy attributes to reference the name and
    parent. This allows you to have nice attribute names for storage in Mongo.

    The main benefit, though is the ability of the object to load its
    location, so that you can load the object without going through the
    container and get full location path.

      >>> class Proxies(container.MongoContainer):
      ...     def __init__(self, name):
      ...         super(Proxies, self).__init__()
      ...         self.name = name
      ...     def __repr__(self):
      ...         return '<Proxies %s>' %self.name

      >>> class Proxy(container.MongoContained, persistent.Persistent):
      ...     _m_name_attr = 'name'
      ...     _m_parent_attr = 'parent'
      ...     def __init__(self, name, parent):
      ...         self.name = name
      ...         self.parent = parent

    Let's create a proxy component and activate the persistence machinery:

      >>> p = Proxy('proxy', Proxies('one'))
      >>> p._p_jar = dm

    So accessing the name and parent works:

      >>> p.__name__
      'proxy'
      >>> p.__parent__
      <Proxies one>

    But assignment is only stored into the volatile variables and the proxy
    attribute values are not touched.

      >>> p.__name__ = 'proxy2'
      >>> p.__name__
      'proxy2'
      >>> p.name
      'proxy'
      >>> p.__parent__ = Proxies('two')
      >>> p.__parent__
      <Proxies two>
      >>> p.parent
      <Proxies one>

    This behavior is intentional, so that containment machinery cannot mess
    with the real attributes. Note that in practice, only MongoContainer sets
    the ``__name__`` and ``__parent__`` and it should be always consistent
    with the referenced attributes.

    """

def doctest_MongoContained_setter_getter():
    """MongoContained: setter/getter functions

    If you need ultimate flexibility of where to get and store the name and
    parent, then you can define setters and getters.

      >>> class Funcs(container.MongoContainer):
      ...     def __init__(self, name):
      ...         super(Funcs, self).__init__()
      ...         self.name = name
      ...     def __repr__(self):
      ...         return '<Funcs %s>' %self.name

      >>> class Func(container.MongoContained, persistent.Persistent):
      ...     _m_name_getter = lambda s: s.name
      ...     _m_name_setter = lambda s, v: setattr(s, 'name', v)
      ...     _m_parent_getter = lambda s: s.parent
      ...     _m_parent_setter = lambda s, v: setattr(s, 'parent', v)
      ...     def __init__(self, name, parent):
      ...         self.name = name
      ...         self.parent = parent

    Let's create a func component and activate the persistence machinery:

      >>> f = Func('func', Funcs('one'))
      >>> f._p_jar = dm

    So accessing the name and parent works:

      >>> f.__name__
      'func'
      >>> f.__parent__
      <Funcs one>

    In this case, the setters are used, if the name and parent are changed:

      >>> f.__name__ = 'func2'
      >>> f.__name__
      'func2'
      >>> f.name
      'func2'
      >>> f.__parent__ = Funcs('two')
      >>> f.__parent__
      <Funcs two>
      >>> f.parent
      <Funcs two>
    """


def doctest_MongoContained_mixed():
    """MongoContained: mixed usage

    When the container is stored in the ZODB or another persistence mechanism,
    a mixed usage of proxy attributes and getter/setter functions is the best
    approach.

      >>> class Mixers(btree.BTreeContainer):
      ...     def __init__(self, name):
      ...         super(Mixers, self).__init__()
      ...         self.name = name
      ...     def __repr__(self):
      ...         return '<Mixers %s>' %self.name
      >>> mixers = Mixers('one')

      >>> class Mixer(container.MongoContained, persistent.Persistent):
      ...     _m_name_attr = 'name'
      ...     _m_parent_getter = lambda s: mixers
      ...     def __init__(self, name):
      ...         self.name = name

    Let's create a mixer component and activate the persistence machinery:

      >>> m = Mixer('mixer')
      >>> m._p_jar = dm

    So accessing the name and parent works:

      >>> m.__name__
      'mixer'
      >>> m.__parent__
      <Mixers one>
    """


def doctest_SimpleMongoContainer_basic():
    """SimpleMongoContainer: basic

      >>> cn = 'mongopersist.zope.container.SimpleMongoContainer'

    Let's make sure events are fired correctly:

      >>> zope.component.provideHandler(handleObjectModifiedEvent)

    Let's add a container to the root:

      >>> dm.reset()
      >>> dm.root['c'] = container.SimpleMongoContainer()

      >>> db = dm._conn[DBNAME]
      >>> pprint(list(db[cn].find()))
      [{u'_id': ObjectId('4e7ea146e13823316f000000'), u'data': {}}]

    As you can see, the serialization is very clean. Next we add a person.

      >>> dm.root['c'][u'stephan'] = SimplePerson(u'Stephan')
      ContainerModifiedEvent: <...SimpleMongoContainer ...>
      >>> dm.root['c'].keys()
      [u'stephan']
      >>> dm.root['c'][u'stephan']
      <SimplePerson Stephan>

      >>> dm.root['c']['stephan'].__parent__
      <mongopersist.zope.container.SimpleMongoContainer object at 0x7fec50f86500>
      >>> dm.root['c']['stephan'].__name__
      u'stephan'

    You can also access objects using the ``get()`` method of course:

      >>> stephan = dm.root['c'].get(u'stephan')
      >>> stephan.__parent__
      <mongopersist.zope.container.SimpleMongoContainer object at 0x7fec50f86500>
      >>> stephan.__name__
      u'stephan'

    Let's commit and access the data again:

      >>> transaction.commit()

      >>> pprint(list(db['person'].find()))
      [{u'__name__': u'stephan',
        u'__parent__':
            DBRef(u'mongopersist.zope.container.SimpleMongoContainer',
                  ObjectId('4e7ddf12e138237403000000'),
                  u'mongopersist_container_test'),
        u'_id': ObjectId('4e7ddf12e138237403000000'),
        u'name': u'Stephan'}]

      >>> dm.root['c'].keys()
      [u'stephan']
      >>> dm.root['c']['stephan'].__parent__
      <mongopersist.zope.container.SimpleMongoContainer object at 0x7fec50f86500>
      >>> dm.root['c']['stephan'].__name__
      u'stephan'

      >>> dm.root['c'].items()
      [(u'stephan', <SimplePerson Stephan>)]

      >>> dm.root['c'].values()
      [<SimplePerson Stephan>]

    Now remove the item:

      >>> del dm.root['c']['stephan']
      ContainerModifiedEvent: <...SimpleMongoContainer ...>

    The changes are immediately visible.

      >>> dm.root['c'].keys()
      []
      >>> dm.root['c']['stephan']
      Traceback (most recent call last):
      ...
      KeyError: 'stephan'

    Make sure it is really gone after committing:

      >>> transaction.commit()
      >>> dm.root['c'].keys()
      []

    The object is also removed from Mongo:

      >>> pprint(list(db['person'].find()))
      []

    Check adding of more objects:

      >>> dm.root['c'][u'roy'] = SimplePerson(u'Roy')
      ContainerModifiedEvent: <...SimpleMongoContainer ...>
      >>> dm.root['c'][u'adam'] = SimplePerson(u'Adam')
      ContainerModifiedEvent: <...SimpleMongoContainer ...>
      >>> dm.root['c'][u'marius'] = SimplePerson(u'Marius')
      ContainerModifiedEvent: <...SimpleMongoContainer ...>

      >>> sorted(dm.root['c'].keys())
      [u'adam', u'marius', u'roy']

    """


def doctest_MongoContainer_basic():
    """MongoContainer: basic

    Let's make sure events are fired correctly:

      >>> zope.component.provideHandler(handleObjectModifiedEvent)

    Let's add a container to the root:

      >>> transaction.commit()
      >>> dm.root['c'] = container.MongoContainer('person')

      >>> db = dm._conn[DBNAME]
      >>> pprint(list(db['mongopersist.zope.container.MongoContainer'].find()))
      [{u'_id': ObjectId('4e7ddf12e138237403000000'),
        u'_m_collection': u'person'}]

    It is unfortunate that the '_m_collection' attribute is set. This is
    avoidable using a sub-class.

      >>> dm.root['c'][u'stephan'] = Person(u'Stephan')
      ContainerModifiedEvent: <...MongoContainer ...>
      >>> dm.root['c'].keys()
      [u'stephan']
      >>> dm.root['c'][u'stephan']
      <Person Stephan>

      >>> dm.root['c']['stephan'].__parent__
      <mongopersist.zope.container.MongoContainer object at 0x7fec50f86500>
      >>> dm.root['c']['stephan'].__name__
      u'stephan'

    It is a feature of the container that the item is immediately available
    after assignment, but before the data is stored in the database. Let's
    commit and access the data again:

      >>> transaction.commit()

      >>> pprint(list(db['person'].find()))
      [{u'_id': ObjectId('4e7e9d3ae138232d7b000003'),
        u'key': u'stephan',
        u'name': u'Stephan',
        u'parent': DBRef(u'mongopersist.zope.container.MongoContainer',
                         ObjectId('4e7e9d3ae138232d7b000000'),
                         u'mongopersist_container_test')}]

      >>> 'stephan' in dm.root['c']
      True
      >>> dm.root['c'].keys()
      [u'stephan']
      >>> dm.root['c']['stephan'].__parent__
      <mongopersist.zope.container.MongoContainer object at 0x7fec50f86500>
      >>> dm.root['c']['stephan'].__name__
      u'stephan'

    We get a usual key error, if an object does not exist:

      >>> dm.root['c']['roy']
      Traceback (most recent call last):
      ...
      KeyError: 'roy'

      >>> 'roy' in dm.root['c']
      False

    Now remove the item:

      >>> del dm.root['c']['stephan']
      ContainerModifiedEvent: <...MongoContainer ...>

    The changes are immediately visible.

      >>> dm.root['c'].keys()
      []
      >>> dm.root['c']['stephan']
      Traceback (most recent call last):
      ...
      KeyError: 'stephan'

    Make sure it is really gone after committing:

      >>> transaction.commit()
      >>> dm.root['c'].keys()
      []

    Check adding of more objects:

      >>> dm.root['c'][u'roy'] = SimplePerson(u'Roy')
      ContainerModifiedEvent: <...MongoContainer ...>
      >>> dm.root['c'][u'adam'] = SimplePerson(u'Adam')
      ContainerModifiedEvent: <...MongoContainer ...>
      >>> dm.root['c'][u'marius'] = SimplePerson(u'Marius')
      ContainerModifiedEvent: <...MongoContainer ...>

      >>> sorted(dm.root['c'].keys())
      [u'adam', u'marius', u'roy']
    """

def doctest_MongoContainer_constructor():
    """MongoContainer: constructor

    The constructor of the MongoContainer class has several advanced arguments
    that allow customizing the storage options.

      >>> transaction.commit()
      >>> c = container.MongoContainer(
      ...     'person',
      ...     database = 'testdb',
      ...     mapping_key = 'name',
      ...     parent_key = 'site')

    The database allows you to specify a custom database in which the items
    are located. Otherwise the datamanager's default database is used.

      >>> c._m_database
      'testdb'

    The mapping key is the key/attribute of the contained items in which their
    name/key within the mapping is stored.

      >>> c._m_mapping_key
      'name'

    The parent key is the key/attribute in which the parent reference is
    stored. This is used to suport multiple containers per Mongo collection.

      >>> c._m_parent_key
      'site'
    """

def doctest_MongoContainer_m_parent_key_value():
    r"""MongoContainer: _m_parent_key_value()

    This method is used to extract the parent reference for the item.

      >>> c = container.MongoContainer('person')

    The default implementation requires the container to be in some sort of
    persistent store, though it does not care whether this store is Mongo or a
    classic ZODB. This feature allows one to mix and match ZODB and Mongo
    storage.

      >>> c._m_get_parent_key_value()
      Traceback (most recent call last):
      ...
      ValueError: _p_jar not found.

    Now the ZODB case:

      >>> c._p_jar = object()
      >>> c._p_oid = '\x00\x00\x00\x00\x00\x00\x00\x01'
      >>> c._m_get_parent_key_value()
      'zodb-0000000000000001'

    And finally the Mongo case:

      >>> c._p_jar = c._p_oid = None
      >>> dm.root['people'] = c
      >>> c._m_get_parent_key_value()
      <mongopersist.zope.container.MongoContainer object at 0x32deed8>

    In that final case, the container itself is returned, because upon
    serialization, we simply look up the dbref.
    """

def doctest_MongoContainer_many_items():
    """MongoContainer: many items

    Let's create an interesting set of data:

      >>> transaction.commit()
      >>> dm.root['people'] = container.MongoContainer('person')
      >>> dm.root['people'][u'stephan'] = Person(u'Stephan')
      >>> dm.root['people'][u'roy'] = Person(u'Roy')
      >>> dm.root['people'][u'roger'] = Person(u'Roger')
      >>> dm.root['people'][u'adam'] = Person(u'Adam')
      >>> dm.root['people'][u'albertas'] = Person(u'Albertas')
      >>> dm.root['people'][u'russ'] = Person(u'Russ')

    In order for find to work, the data has to be committed:

      >>> transaction.commit()

    Let's now search and receive documents as result:

      >>> sorted(dm.root['people'].keys())
      [u'adam', u'albertas', u'roger', u'roy', u'russ', u'stephan']
      >>> dm.root['people'][u'stephan']
      <Person Stephan>
      >>> dm.root['people'][u'adam']
      <Person Adam>
"""

def doctest_MongoContainer_setitem_with_no_key_MongoContainer():
    """MongoContainer: __setitem__(None, obj)

    Whenever an item is added with no key, getattr(obj, _m_mapping_key) is used.

      >>> transaction.commit()
      >>> dm.root['people'] = container.MongoContainer(
      ...     'person', mapping_key='name')
      >>> dm.root['people'][None] = Person(u'Stephan')

    Let's now search and receive documents as result:

      >>> sorted(dm.root['people'].keys())
      [u'...']
      >>> stephan = dm.root['people'].values()[0]
      >>> stephan.__name__ == str(stephan.name)
      True
"""

def doctest_MongoContainer_setitem_with_no_key_IdNamesMongoContainer():
    """IdNamesMongoContainer: __setitem__(None, obj)

    Whenever an item is added with no key, the OID is used.

      >>> transaction.commit()
      >>> dm.root['people'] = container.IdNamesMongoContainer('person')
      >>> dm.root['people'][None] = Person(u'Stephan')

    Let's now search and receive documents as result:

      >>> sorted(dm.root['people'].keys())
      [u'...']
      >>> stephan = dm.root['people'].values()[0]
      >>> stephan.__name__ == str(stephan._p_oid.id)
      True
"""

def doctest_MongoContainer_add_MongoContainer():
    """MongoContainer: add(value, key=None)

    Sometimes we just do not want to be responsible to determine the name of
    the object to be added. This method makes this optional. The default
    implementation assigns getattr(obj, _m_mapping_key) as name:

      >>> transaction.commit()
      >>> dm.root['people'] = container.MongoContainer(
      ...     'person', mapping_key='name')
      >>> dm.root['people'].add(Person(u'Stephan'))

    Let's now search and receive documents as result:

      >>> sorted(dm.root['people'].keys())
      [u'...']
      >>> stephan = dm.root['people'].values()[0]
      >>> stephan.__name__ == str(stephan.name)
      True
"""

def doctest_MongoContainer_add_IdNamesMongoContainer():
    """IdNamesMongoContainer: add(value, key=None)

    Sometimes we just do not want to be responsible to determine the name of
    the object to be added. This method makes this optional. The default
    implementation assigns the OID as name:

      >>> transaction.commit()
      >>> dm.root['people'] = container.IdNamesMongoContainer('person')
      >>> dm.root['people'].add(Person(u'Stephan'))

    Let's now search and receive documents as result:

      >>> sorted(dm.root['people'].keys())
      [u'...']
      >>> stephan = dm.root['people'].values()[0]
      >>> stephan.__name__ == str(stephan._p_oid.id)
      True
"""

def doctest_MongoContainer_find():
    """MongoContainer: find

    The Mongo Container supports direct Mongo queries. It does, however,
    insert the additional container filter arguments and can optionally
    convert the documents to objects.

    Let's create an interesting set of data:

      >>> transaction.commit()
      >>> dm.root['people'] = container.MongoContainer('person')
      >>> dm.root['people'][u'stephan'] = Person(u'Stephan')
      >>> dm.root['people'][u'roy'] = Person(u'Roy')
      >>> dm.root['people'][u'roger'] = Person(u'Roger')
      >>> dm.root['people'][u'adam'] = Person(u'Adam')
      >>> dm.root['people'][u'albertas'] = Person(u'Albertas')
      >>> dm.root['people'][u'russ'] = Person(u'Russ')

    In order for find to work, the data has to be committed:

      >>> transaction.commit()

    Let's now search and receive documents as result:

      >>> res = dm.root['people'].raw_find({'name': {'$regex': '^Ro.*'}})
      >>> pprint(list(res))
      [{u'_id': ObjectId('4e7eb152e138234158000004'),
        u'key': u'roy',
        u'name': u'Roy',
        u'parent': DBRef(u'mongopersist.zope.container.MongoContainer',
                         ObjectId('4e7eb152e138234158000000'),
                         u'mongopersist_container_test')},
       {u'_id': ObjectId('4e7eb152e138234158000005'),
        u'key': u'roger',
        u'name': u'Roger',
        u'parent': DBRef(u'mongopersist.zope.container.MongoContainer',
                         ObjectId('4e7eb152e138234158000000'),
                         u'mongopersist_container_test')}]

    And now the same query, but this time with object results:

      >>> res = dm.root['people'].find({'name': {'$regex': '^Ro.*'}})
      >>> pprint(list(res))
      [<Person Roy>, <Person Roger>]

    When no spec is specified, all items are returned:

      >>> res = dm.root['people'].find()
      >>> pprint(list(res))
      [<Person Stephan>, <Person Roy>, <Person Roger>, <Person Adam>,
       <Person Albertas>, <Person Russ>]

    You can also search for a single result:

      >>> res = dm.root['people'].raw_find_one({'name': {'$regex': '^St.*'}})
      >>> pprint(res)
      {u'_id': ObjectId('4e7eb259e138234289000003'),
       u'key': u'stephan',
       u'name': u'Stephan',
       u'parent': DBRef(u'mongopersist.zope.container.MongoContainer',
                        ObjectId('4e7eb259e138234289000000'),
                        u'mongopersist_container_test')}

      >>> stephan = dm.root['people'].find_one({'name': {'$regex': '^St.*'}})
      >>> pprint(stephan)
      <Person Stephan>

    If no result is found, ``None`` is returned:

      >>> dm.root['people'].find_one({'name': {'$regex': '^XXX.*'}})

    If there is no spec, then simply the first item is returned:

      >>> dm.root['people'].find_one()
      <Person Stephan>

    On the other hand, if the spec is an id, we look for it instead:

      >>> dm.root['people'].find_one(stephan._p_oid.id)
      <Person Stephan>
    """

def doctest_IdNamesMongoContainer_basic():
    """IdNamesMongoContainer: basic

    This container uses the Mongo ObjectId as the name for each object. Since
    ObjectIds are required to be unique within a collection, this is actually
    a nice and cheap scenario.

    Let's add a container to the root:

      >>> transaction.commit()
      >>> dm.root['c'] = container.IdNamesMongoContainer('person')

    Let's now add a new person:

      >>> dm.root['c'].add(Person(u'Stephan'))
      >>> keys = dm.root['c'].keys()
      >>> keys
      [u'4e7ddf12e138237403000003']
      >>> name = keys[0]
      >>> dm.root['c'][name]
      <Person Stephan>

      >>> dm.root['c'].values()
      [<Person Stephan>]

      >>> dm.root['c'][name].__parent__
      <mongopersist.zope.container.IdNamesMongoContainer object at 0x7fec50f86500>
      >>> dm.root['c'][name].__name__
      u'4e7ddf12e138237403000003'

    It is a feature of the container that the item is immediately available
    after assignment, but before the data is stored in the database. Let's
    commit and access the data again:

      >>> transaction.commit()

      >>> db = dm._conn[DBNAME]
      >>> pprint(list(db['person'].find()))
      [{u'_id': ObjectId('4e7e9d3ae138232d7b000003'),
        u'name': u'Stephan',
        u'parent': DBRef(u'mongopersist.zope.container.IdNamesMongoContainer',
                         ObjectId('4e7e9d3ae138232d7b000000'),
                         u'mongopersist_container_test')}]

    Notice how there is no "key" entry in the document. We get a usual key
    error, if an object does not exist:

      >>> dm.root['c']['4e7e9d3ae138232d7b000fff']
      Traceback (most recent call last):
      ...
      KeyError: '4e7e9d3ae138232d7b000fff'

      >>> '4e7e9d3ae138232d7b000fff' in dm.root['c']
      False

      >>> dm.root['c']['roy']
      Traceback (most recent call last):
      ...
      KeyError: 'roy'

      >>> 'roy' in dm.root['c']
      False

    Now remove the item:

      >>> del dm.root['c'][name]

    The changes are immediately visible.

      >>> dm.root['c'].keys()
      []
      >>> dm.root['c'][name]
      Traceback (most recent call last):
      ...
      KeyError: u'4e7e9d3ae138232d7b000003'

    Make sure it is really gone after committing:

      >>> transaction.commit()
      >>> dm.root['c'].keys()
      []
    """

def doctest_AllItemsMongoContainer_basic():
    """AllItemsMongoContainer: basic

    This type of container returns all items of the collection without regard
    of a parenting hierarchy.

    Let's start by creating two person containers that service different
    purposes:

      >>> transaction.commit()

      >>> dm.root['friends'] = container.MongoContainer('person')
      >>> dm.root['friends'][u'roy'] = Person(u'Roy')
      >>> dm.root['friends'][u'roger'] = Person(u'Roger')

      >>> dm.root['family'] = container.MongoContainer('person')
      >>> dm.root['family'][u'anton'] = Person(u'Anton')
      >>> dm.root['family'][u'konrad'] = Person(u'Konrad')

      >>> transaction.commit()
      >>> sorted(dm.root['friends'].keys())
      [u'roger', u'roy']
      >>> sorted(dm.root['family'].keys())
      [u'anton', u'konrad']

    Now we can create an all-items-container that allows us to view all
    people.

      >>> dm.root['all-people'] = container.AllItemsMongoContainer('person')
      >>> sorted(dm.root['all-people'].keys())
      [u'anton', u'konrad', u'roger', u'roy']
    """

def doctest_SubDocumentMongoContainer_basic():
    r"""SubDocumentMongoContainer: basic

    Let's make sure events are fired correctly:

      >>> zope.component.provideHandler(handleObjectModifiedEvent)

    Sub_document Mongo containers are useful, since they avoid the creation of
    a commonly trivial collections holding meta-data for the collection
    object. But they require a root document:

      >>> dm.reset()
      >>> dm.root['app_root'] = ApplicationRoot()

    Let's add a container to the app root:

      >>> dm.root['app_root']['people'] = \
      ...     container.SubDocumentMongoContainer('person')
      ContainerModifiedEvent: <ApplicationRoot>

      >>> transaction.commit()
      >>> db = dm._conn[DBNAME]
      >>> pprint(list(db['root'].find()))
      [{u'_id': ObjectId('4e7ea67be138233711000001'),
        u'data':
         {u'people':
          {u'_m_collection': u'person',
           u'_py_persistent_type':
               u'mongopersist.zope.container.SubDocumentMongoContainer'}}}]

    It is unfortunate that the '_m_collection' attribute is set. This is
    avoidable using a sub-class. Let's make sure the container can be loaded
    correctly:

      >>> dm.root['app_root']['people']
      <mongopersist.zope.container.SubDocumentMongoContainer ...>
      >>> dm.root['app_root']['people'].__parent__
      <ApplicationRoot>
      >>> dm.root['app_root']['people'].__name__
      'people'

    Let's add an item to the container:

      >>> dm.root['app_root']['people'][u'stephan'] = Person(u'Stephan')
      ContainerModifiedEvent: <...SubDocumentMongoContainer ...>
      >>> dm.root['app_root']['people'].keys()
      [u'stephan']
      >>> dm.root['app_root']['people'][u'stephan']
      <Person Stephan>

      >>> transaction.commit()
      >>> dm.root['app_root']['people'].keys()
      [u'stephan']
    """

def doctest_MongoContainer_with_ZODB():
    r"""MongoContainer: with ZODB

    This test demonstrates how a Mongo Container lives inside a ZODB tree:

      >>> zodb = ZODB.DB(ZODB.DemoStorage.DemoStorage())
      >>> root = zodb.open().root()
      >>> root['app'] = btree.BTreeContainer()
      >>> root['app']['people'] = container.MongoContainer('person')

    Let's now commit the transaction and make sure everything is cool.

      >>> transaction.commit()
      >>> root = zodb.open().root()
      >>> root['app']
      <zope.container.btree.BTreeContainer object at 0x7fbb5842f578>
      >>> root['app']['people']
      <mongopersist.zope.container.MongoContainer object at 0x7fd6e23555f0>

    Trying accessing people fails:

      >>> root['app']['people'].keys()
      Traceback (most recent call last):
      ...
      ComponentLookupError:
       (<InterfaceClass mongopersist.interfaces.IMongoDataManagerProvider>, '')

    This is because we have not told the system how to get a datamanager:

      >>> class Provider(object):
      ...     zope.interface.implements(interfaces.IMongoDataManagerProvider)
      ...     def get(self):
      ...         return dm
      >>> zope.component.provideUtility(Provider())

    So let's try again:

      >>> root['app']['people'].keys()
      []

    Next we create a person object and make sure it gets properly persisted.

      >>> root['app']['people']['stephan'] = Person(u'Stephan')
      >>> transaction.commit()
      >>> root = zodb.open().root()
      >>> root['app']['people'].keys()
      [u'stephan']

      >>> stephan = root['app']['people']['stephan']
      >>> stephan.__name__
      u'stephan'
      >>> stephan.__parent__
      <mongopersist.zope.container.MongoContainer object at 0x7f6b6273b7d0>

      >>> pprint(list(dm._get_collection(DBNAME, 'person').find()))
      [{u'_id': ObjectId('4e7ed795e1382366a0000001'),
        u'key': u'stephan',
        u'name': u'Stephan',
        u'parent': u'zodb-1058e89d27d8afd9'}]

    Note that we produced a nice hex-presentation of the ZODB's OID.
    """


# classes for doctest_Realworldish
class Campaigns(container.MongoContainer):
    _m_collection = 'campaigns'

    def __init__(self, name):
        self.name = name

    def add(self, campaign):
        self[campaign.name] = campaign

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)


class MongoItem(container.MongoContained,
                persistent.Persistent):
    pass


class Campaign(MongoItem, container.MongoContainer):
    _m_collection = 'persons'
    _p_mongo_collection = 'campaigns'

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)


class PersonItem(MongoItem):
    _p_mongo_collection = 'persons'

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)


def doctest_Realworldish():
    """Let's see some real worldish hierarchic structure persisted

    Let's make sure events are fired correctly:

      >>> zope.component.provideHandler(handleObjectModifiedEvent)

    Let's add a container to the root:

      >>> transaction.commit()
      >>> dm.root['c'] = Campaigns('foobar')

      >>> db = dm._conn[DBNAME]
      >>> pprint(list(db['mongopersist.zope.tests.test_container.Campaigns'].find()))
      [{u'_id': ObjectId('4e7ddf12e138237403000000'),
        u'name': u'foobar'}]

    It is unfortunate that the '_m_collection' attribute is set. This is
    avoidable using a sub-class.

      >>> dm.root['c'][u'one'] = Campaign(u'one')
      ContainerModifiedEvent: <...Campaigns ...>
      >>> dm.root['c'].keys()
      [u'one']
      >>> dm.root['c'][u'one']
      <Campaign one>

      >>> dm.root['c']['one'].__parent__
      <Campaigns foobar>
      >>> dm.root['c']['one'].__name__
      u'one'

    It is a feature of the container that the item is immediately available
    after assignment, but before the data is stored in the database. Let's
    commit and access the data again:

      >>> transaction.commit()

      >>> pprint(list(db['campaigns'].find()))
      [{u'_id': ObjectId('4e7ddf12e138237403000000'),
        u'key': u'one',
        u'name': u'one',
        u'parent': DBRef(u'mongopersist.zope.tests.test_container.Campaigns',
            ObjectId('4e7ddf12e138237403000000'),
            u'mongopersist_container_test')}]

      >>> 'one' in dm.root['c']
      True
      >>> dm.root['c'].keys()
      [u'one']
      >>> dm.root['c']['one'].__parent__
      <Campaigns foobar>
      >>> dm.root['c']['one'].__name__
      u'one'

    We get a usual key error, if an object does not exist:

      >>> dm.root['c']['roy']
      Traceback (most recent call last):
      ...
      KeyError: 'roy'

      >>> 'roy' in dm.root['c']
      False

    Now remove the item:

      >>> del dm.root['c']['one']
      ContainerModifiedEvent: <...Campaigns ...>

    The changes are immediately visible.

      >>> dm.root['c'].keys()
      []
      >>> dm.root['c']['one']
      Traceback (most recent call last):
      ...
      KeyError: 'one'

    Make sure it is really gone after committing:

      >>> transaction.commit()
      >>> dm.root['c'].keys()
      []

    Check adding of more objects:

      >>> dm.root['c'][u'1'] = c1 = Campaign(u'One')
      ContainerModifiedEvent: <...Campaigns ...>
      >>> dm.root['c'][u'2'] = c2 = Campaign(u'Two')
      ContainerModifiedEvent: <...Campaigns ...>
      >>> dm.root['c'][u'3'] = Campaign(u'Three')
      ContainerModifiedEvent: <...Campaigns ...>

      >>> sorted(dm.root['c'].keys())
      [u'1', u'2', u'3']

    Check adding of more subitems:

      >>> stephan = c1['stephan'] = PersonItem('Stephan')
      ContainerModifiedEvent: <Campaign One>
      >>> roy = c1['roy'] = PersonItem('Roy')
      ContainerModifiedEvent: <Campaign One>

      >>> sorted(c1.keys())
      [u'roy', u'stephan']

      >>> adam = c2['adam'] = PersonItem('Adam')
      ContainerModifiedEvent: <Campaign Two>

      >>> sorted(c1.keys())
      [u'roy', u'stephan']
      >>> sorted(c2.keys())
      [u'adam']

    """


class People(container.AllItemsMongoContainer):
    _m_mapping_key = 'name'
    _p_mongo_collection = 'people'
    _m_collection = 'person'


class Address(persistent.Persistent):
    _p_mongo_collection = 'address'

    def __init__(self, city):
        self.city = city


class PeoplePerson(persistent.Persistent, container.MongoContained):
    _p_mongo_collection = 'person'
    _p_mongo_store_type = True

    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.address = Address('Boston %i' %age)

    def __repr__(self):
        return '<%s %s @ %i [%s]>' %(
            self.__class__.__name__, self.name, self.age, self.__name__)


def doctest_load_does_not_set_p_changed():
    """We need to guarantee that _p_changed is not True on obj load

    Let's add some objects:

      >>> transaction.commit()
      >>> dm.root['people'] = people = People()
      >>> x = transaction.begin()
      >>> for idx in xrange(2):
      ...     people[None] = PeoplePerson('Mr Number %.5i' %idx, random.randint(0, 100))
      >>> transaction.commit()

      >>> objs = [o for o in people.values()]
      >>> len(objs)
      2
      >>> [o._p_changed for o in objs]
      [False, False]

      >>> [o._p_changed for o in people.values()]
      [False, False]

      >>> transaction.commit()

      >>> x = transaction.begin()
      >>> [o._p_changed for o in people.values()]
      [False, False]

      >>> [o._p_changed for o in people.values()]
      [False, False]

    """


def doctest_firing_events_MongoContainer():
    """Events need to be fired when _m_mapping_key is already set on the object
    and the object gets added to the container

      >>> @zope.component.adapter(zope.component.interfaces.IObjectEvent)
      ... def eventHandler(event):
      ...     print event

      >>> zope.component.provideHandler(eventHandler)

    Let's add some objects:

      >>> transaction.commit()
      >>> dm.root['people'] = people = People()
      >>> x = transaction.begin()
      >>> for idx in xrange(2):
      ...     people[None] = PeoplePerson('Mr Number %.5i' %idx, random.randint(0, 100))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'Mr Number 00000', u'Mr Number 00001']

      >>> for idx in xrange(2):
      ...     name = 'Mr Number %.5i' % (idx+10, )
      ...     people.add(PeoplePerson(name, random.randint(0, 100)))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'Mr Number 00000', u'Mr Number 00001', u'Mr Number 00010', u'Mr Number 00011']

      >>> for idx in xrange(2):
      ...     name = 'Mr Number %.5i' % (idx+20, )
      ...     people[name] = PeoplePerson(name, random.randint(0, 100))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'Mr Number 00000', u'Mr Number 00001', u'Mr Number 00010', u'Mr Number 00011',
       u'Mr Number 00020', u'Mr Number 00021']

    """


class PeopleWithIDKeys(container.IdNamesMongoContainer):
    _p_mongo_collection = 'people'
    _m_collection = 'person'


def doctest_firing_events_IdNamesMongoContainer():
    """Events need to be fired when the object gets added to the container

      >>> @zope.component.adapter(zope.component.interfaces.IObjectEvent)
      ... def eventHandler(event):
      ...     print event

      >>> zope.component.provideHandler(eventHandler)

    Let's add some objects:

      >>> transaction.commit()
      >>> dm.root['people'] = people = PeopleWithIDKeys()
      >>> x = transaction.begin()
      >>> for idx in xrange(2):
      ...     people[None] = PeoplePerson('Mr Number %.5i' %idx, random.randint(0, 100))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000']

      >>> for idx in xrange(2):
      ...     name = 'Mr Number %.5i' % (idx+10, )
      ...     people.add(PeoplePerson(name, random.randint(0, 100)))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000']

      >>> for idx in xrange(2):
      ...     name = 'Mr Number %.5i' % (idx+20, )
      ...     people[name] = PeoplePerson(name, random.randint(0, 100))
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      <zope.lifecycleevent.ObjectAddedEvent object at ...>
      <zope.container.contained.ContainerModifiedEvent object at ...>
      >>> transaction.commit()
      >>> list(people.keys())
      [u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000', u'4e7ddf12e138237403000000']

    """

checker = renormalizing.RENormalizing([
    (re.compile(r'datetime.datetime(.*)'),
     'datetime.datetime(2011, 10, 1, 9, 45)'),
    (re.compile(r"ObjectId\('[0-9a-f]{24}'\)"),
     "ObjectId('4e7ddf12e138237403000000')"),
    (re.compile(r"u'[0-9a-f]{24}'"),
     "u'4e7ddf12e138237403000000'"),
    (re.compile(r"object at 0x[0-9a-f]*>"),
     "object at 0x001122>"),
    (re.compile(r"zodb-[0-9a-f].*"),
     "zodb-01af3b00c5"),
    ])

@zope.component.adapter(
    zope.interface.Interface,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent
    )
def handleObjectModifiedEvent(object, event):
    print event.__class__.__name__+':', repr(object)


def dropDB():
    testing.getConnection().drop_database(DBNAME)


def setUp(test):
    placelesssetup.setUp(test)
    module.setUp(test)
    test.globs['conn'] = testing.getConnection()
    test.globs['DBNAME'] = DBNAME
    testing.cleanDB(test.globs['conn'], test.globs['DBNAME'])
    test.globs['dm'] = datamanager.MongoDataManager(
        test.globs['conn'],
        default_database=test.globs['DBNAME'],
        root_database=test.globs['DBNAME'])

    # silence this, otherwise half-baked objects raise exceptions
    # on trying to __repr__ missing attributes
    test.orig_DEBUG_EXCEPTION_FORMATTER = \
        exceptionformatter.DEBUG_EXCEPTION_FORMATTER
    exceptionformatter.DEBUG_EXCEPTION_FORMATTER = 0


def tearDown(test):
    placelesssetup.tearDown(test)
    module.tearDown(test)
    testing.cleanDB(test.globs['conn'], test.globs['DBNAME'])
    test.globs['conn'].disconnect()
    testing.resetCaches()
    exceptionformatter.DEBUG_EXCEPTION_FORMATTER = \
        test.orig_DEBUG_EXCEPTION_FORMATTER


def test_suite():
    return doctest.DocTestSuite(
        setUp=setUp, tearDown=tearDown, checker=checker,
        optionflags=(doctest.NORMALIZE_WHITESPACE|
                     doctest.ELLIPSIS|
                     doctest.REPORT_ONLY_FIRST_FAILURE
                     #|doctest.REPORT_NDIFF
                     )
        )

atexit.register(dropDB)
