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
"""Mongo Persistence Testing Support"""
from __future__ import absolute_import
import atexit
import doctest
import pymongo
import re
import transaction
from zope.testing import cleanup, module, renormalizing

from mongopersist import datamanager, serialize

checker = renormalizing.RENormalizing([
    (re.compile(r'datetime.datetime(.*)'),
     'datetime.datetime(2011, 10, 1, 9, 45)'),
    (re.compile(r"ObjectId\('[0-9a-f]{24}'\)"),
     "ObjectId('4e7ddf12e138237403000000')"),
    (re.compile(r"u'[0-9a-f]{24}'"),
     "u'4e7ddf12e138237403000000'"),
    (re.compile(r"object at 0x[0-9a-f]*>"),
     "object at 0x001122>"),
    ])

OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_ONLY_FIRST_FAILURE
               #|doctest.REPORT_NDIFF
               )

DBNAME = 'mongopersist_test'


def getConnection():
    return pymongo.Connection('localhost', 27017, tz_aware=False,
                              fsync=False, j=False)


def cleanDB(conn, dbname):
    db = conn[dbname]
    for cname in db.collection_names():
        try:
            db.drop_collection(cname)
        except:
            pass


def dropDB():
    getConnection().drop_database(DBNAME)


def setUp(test):
    module.setUp(test)
    test.globs['conn'] = getConnection()
    test.globs['DBNAME'] = DBNAME
    cleanDB(test.globs['conn'], test.globs['DBNAME'])
    test.globs['commit'] = transaction.commit
    test.globs['dm'] = datamanager.MongoDataManager(
        test.globs['conn'],
        default_database=test.globs['DBNAME'],
        root_database=test.globs['DBNAME'])


def tearDown(test):
    module.tearDown(test)
    transaction.abort()
    cleanDB(test.globs['conn'], test.globs['DBNAME'])
    test.globs['conn'].disconnect()
    resetCaches()


def resetCaches():
    serialize.SERIALIZERS.__init__()
    serialize.OID_CLASS_LRU.__init__(20000)
    serialize.COLLECTIONS_WITH_TYPE.__init__()
    serialize.AVAILABLE_NAME_MAPPINGS.__init__()
    serialize.PATH_RESOLVE_CACHE = {}

cleanup.addCleanUp(resetCaches)
atexit.register(dropDB)
