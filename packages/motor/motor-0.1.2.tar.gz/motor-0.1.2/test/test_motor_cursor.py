# Copyright 2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test Motor, an asynchronous driver for MongoDB and Tornado."""

from __future__ import with_statement

import sys
import time
import unittest
import warnings

import greenlet
import pymongo
from nose.plugins.skip import SkipTest
from tornado import ioloop, gen
from pymongo.errors import InvalidOperation, ConfigurationError, OperationFailure

import motor
from test import host, port, MotorTest, async_test_engine, AssertEqual


class MotorCursorTest(MotorTest):
    def test_cursor(self):
        cx = self.motor_client(host, port)
        coll = cx.pymongo_test.test_collection
        cursor = coll.find()
        self.assertTrue(isinstance(cursor, motor.MotorCursor))
        self.assertFalse(cursor.started, "Cursor shouldn't start immediately")

    @async_test_engine()
    def test_count(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        self.check_required_callback(coll.find().count)
        yield AssertEqual(200, coll.find().count)
        yield AssertEqual(100, coll.find({'_id': {'$gt': 99}}).count)
        where = 'this._id % 2 == 0 && this._id >= 50'
        yield AssertEqual(75, coll.find({'$where': where}).count)
        yield AssertEqual(75, coll.find().where(where).count)
        yield AssertEqual(
            25,
            coll.find({'_id': {'$lt': 100}}).where(where).count)
        yield AssertEqual(
            25,
            coll.find({'_id': {'$lt': 100}, '$where': where}).count)
        done()

    @async_test_engine()
    def test_distinct(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        self.check_required_callback(coll.find().distinct, '_id')
        self.assertEqual(set(range(10)), set((
            yield motor.Op(coll.find({'_id': {'$lt': 10}}).distinct, '_id'))))
        done()

    @async_test_engine()
    def test_fetch_next(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        # 200 results, only including _id field, sorted by _id
        cursor = coll.find({}, {'_id': 1}).sort(
            [('_id', pymongo.ASCENDING)]).batch_size(75)

        self.assertEqual(None, cursor.cursor_id)
        self.assertEqual(None, cursor.next_object()) # Haven't fetched yet
        i = 0
        while (yield cursor.fetch_next):
            self.assertEqual({'_id': i}, cursor.next_object())
            i += 1
            # With batch_size 75 and 200 results, cursor should be exhausted on
            # the server by third fetch
            if i <= 150:
                self.assertNotEqual(0, cursor.cursor_id)
            else:
                self.assertEqual(0, cursor.cursor_id)

        self.assertEqual(False, (yield cursor.fetch_next))
        self.assertEqual(None, cursor.next_object())
        self.assertEqual(0, cursor.cursor_id)
        self.assertEqual(200, i)

        # Decref'ing the cursor eventually closes it on the server; yielding
        # clears the engine Runner's reference to the cursor.
        cursor = coll.find()
        yield cursor.fetch_next
        del cursor
        yield gen.Task(ioloop.IOLoop.instance().add_callback)
        yield gen.Task(self.wait_for_cursors)
        done()

    @async_test_engine()
    def test_fetch_next_without_results(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        # Nothing matches this query
        cursor = coll.find({'foo':'bar'})
        self.assertEqual(None, cursor.next_object())
        self.assertEqual(False, (yield cursor.fetch_next))
        self.assertEqual(None, cursor.next_object())
        # Now cursor knows it's exhausted
        self.assertEqual(0, cursor.cursor_id)
        done()

    @async_test_engine()
    def test_fetch_next_is_idempotent(self, done):
        # Subsequent calls to fetch_next don't do anything
        coll = self.motor_client(host, port).pymongo_test.test_collection
        cursor = coll.find()
        self.assertEqual(None, cursor.cursor_id)
        yield cursor.fetch_next
        self.assertTrue(cursor.cursor_id)
        self.assertEqual(101, cursor._buffer_size())
        yield cursor.fetch_next  # Does nothing
        self.assertEqual(101, cursor._buffer_size())
        done()

    @async_test_engine()
    def test_each(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        self.check_required_callback(coll.find().each)
        cursor = coll.find({}, {'_id': 1}).sort([('_id', pymongo.ASCENDING)])
        yield_point = yield gen.Callback(0)
        results = []
        def callback(result, error):
            if error:
                raise error

            results.append(result)
            if not result:
                yield_point()

        cursor.each(callback)
        yield gen.Wait(0)
        expected = [{'_id': i} for i in range(200)] + [None]
        self.assertEqual(expected, results)
        done()

    def test_to_list_argument_checking(self):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        cursor = coll.find()
        self.check_required_callback(cursor.to_list, 10)

        cursor = coll.find()
        callback = lambda result, error: None
        self.assertRaises(ConfigurationError, cursor.to_list, -1, callback)
        self.assertRaises(ConfigurationError, cursor.to_list, 'foo', callback)

    @async_test_engine()
    def test_to_list(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        cursor = coll.find({}, {'_id': 1}).sort([('_id', pymongo.ASCENDING)])
        expected = [{'_id': i} for i in range(200)]
        yield AssertEqual(expected, cursor.to_list, length=1000)
        yield motor.Op(cursor.close)
        done()

    def test_to_list_length_warning(self):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        callback = lambda result, error: None

        if sys.version_info[:2] < (2, 6):
            raise SkipTest("Too annoying to test warnings in Python 2.5")

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            coll.find().to_list(length=None, callback=callback)
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[0].category, RuntimeWarning))

            # No warnings
            coll.find().to_list(length=0, callback=callback)
            coll.find().to_list(length=1, callback=callback)
            coll.find().limit(1).to_list(length=None, callback=callback)
            coll.find().to_list(length=None, callback=callback)

    @async_test_engine()
    def test_to_list_with_length(self, done):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        cursor = coll.find({}, {'_id': 1}).sort([('_id', pymongo.ASCENDING)])
        yield AssertEqual([], cursor.to_list, 0)

        def expected(start, stop):
            return [{'_id': i} for i in range(start, stop)]

        yield AssertEqual(expected(0, 10), cursor.to_list, 10)
        yield AssertEqual(expected(10, 100), cursor.to_list, 90)

        # Test particularly rigorously around the 101-doc mark, since this is
        # where the first batch ends
        yield AssertEqual(expected(100, 101), cursor.to_list, 1)
        yield AssertEqual(expected(101, 102), cursor.to_list, 1)
        yield AssertEqual(expected(102, 103), cursor.to_list, 1)
        yield AssertEqual([], cursor.to_list, 0)
        yield AssertEqual(expected(103, 105), cursor.to_list, 2)

        # Only 95 docs left, make sure length=100 doesn't error or hang
        yield AssertEqual(expected(105, 200), cursor.to_list, 100)
        self.assertEqual(0, cursor.cursor_id)

        # Check that passing None explicitly is the same as no length
        result = yield motor.Op(coll.find().to_list, None)
        self.assertEqual(200, len(result))
        done()

    def test_to_list_tailable(self):
        coll = self.motor_client(host, port).pymongo_test.test_collection
        cursor = coll.find(tailable=True)

        # Can't call to_list on tailable cursor
        self.assertRaises(InvalidOperation,
            cursor.to_list, callback=lambda result, error: None)

    @async_test_engine()
    def test_limit_zero(self, done):
        # Limit of 0 is a weird case that PyMongo handles specially, make sure
        # Motor does too. cursor.limit(0) means "remove limit", but cursor[:0]
        # or cursor[5:5] sets the cursor to "empty".
        coll = self.motor_client(host, port).pymongo_test.test_collection

        # Make sure our setup code made some documents
        results = yield motor.Op(coll.find().to_list, length=1000)
        self.assertTrue(len(results) > 0)
        self.assertEqual(False, (yield coll.find()[:0].fetch_next))
        self.assertEqual(False, (yield coll.find()[5:5].fetch_next))
        yield AssertEqual(None, coll.find()[:0].each)
        yield AssertEqual(None, coll.find()[5:5].each)
        yield AssertEqual([], coll.find()[:0].to_list)
        yield AssertEqual([], coll.find()[5:5].to_list)
        done()

    @async_test_engine()
    def test_cursor_explicit_close(self, done):
        cx = self.motor_client(host, port)
        collection = cx.pymongo_test.test_collection
        self.check_optional_callback(collection.find().close)
        cursor = collection.find()
        yield cursor.fetch_next
        self.assertTrue(cursor.alive)
        yield motor.Op(cursor.close)

        # Cursor reports it's alive because it has buffered data, even though
        # it's killed on the server
        self.assertTrue(cursor.alive)
        yield gen.Task(self.wait_for_cursors)
        done()

    def test_each_cancel(self):
        loop = ioloop.IOLoop.instance()
        cx = self.motor_client(host, port)
        collection = cx.pymongo_test.test_collection
        results = []

        def cancel(result, error):
            if error:
                loop.stop()
                raise error

            results.append(result)
            loop.add_callback(canceled)
            return False # Cancel iteration

        def canceled():
            try:
                self.assertFalse(cursor.delegate._Cursor__killed)
                self.assertTrue(cursor.alive)

                # Resume iteration
                cursor.each(each)
            except Exception:
                loop.stop()
                raise

        def each(result, error):
            if error:
                loop.stop()
                raise error

            if result:
                results.append(result)
            else:
                # Complete
                loop.stop()

        cursor = collection.find()
        cursor.each(cancel)
        loop.start()

        self.assertEqual(self.sync_coll.count(), len(results))

    def test_cursor_slice_argument_checking(self):
        cx = self.motor_client(host, port)
        collection = cx.pymongo_test.test_collection

        for arg in '', None, {}, []:
            self.assertRaises(TypeError, lambda: collection.find()[arg])

        self.assertRaises(IndexError, lambda: collection.find()[-1])

    @async_test_engine()
    def test_cursor_slice(self, done):
        # This is an asynchronous copy of PyMongo's test_getitem_slice_index in
        # test_cursor.py
        warnings.simplefilter("ignore")

        cx = self.motor_client(host, port)

        # test_collection was filled out in setUp()
        coll = cx.pymongo_test.test_collection

        self.assertRaises(IndexError, lambda: coll.find()[-1])
        self.assertRaises(IndexError, lambda: coll.find()[1:2:2])
        self.assertRaises(IndexError, lambda: coll.find()[2:1])

        # Since the cursor has no limit in this test, important to pass length
        # and avoid raising to_list's RuntimeWarning; otherwise it isn't raised
        # again and test_to_list_length_warning fails.
        result = yield motor.Op(coll.find()[0:].to_list, length=1000)
        self.assertEqual(200, len(result))

        result = yield motor.Op(coll.find()[20:].to_list, length=1000)
        self.assertEqual(180, len(result))

        result = yield motor.Op(coll.find()[99:].to_list, length=1000)
        self.assertEqual(101, len(result))

        result = yield motor.Op(coll.find()[1000:].to_list, length=1000)
        self.assertEqual(0, len(result))

        result = yield motor.Op(coll.find()[20:25].to_list)
        self.assertEqual(5, len(result))

        # Any slice overrides all previous slices
        result = yield motor.Op(coll.find()[20:25][20:].to_list, length=1000)
        self.assertEqual(180, len(result))

        result = yield motor.Op(coll.find()[20:25].limit(0).skip(20).to_list, length=1000)
        self.assertEqual(180, len(result))

        result = yield motor.Op(coll.find().limit(0).skip(20)[20:25].to_list)
        self.assertEqual(5, len(result))

        result = yield motor.Op(coll.find()[:1].to_list)
        self.assertEqual(1, len(result))

        result = yield motor.Op(coll.find()[:5].to_list)
        self.assertEqual(5, len(result))

        done()

    @async_test_engine()
    def test_cursor_index(self, done):
        cx = self.motor_client(host, port)

        # test_collection was filled out in setUp() with 200 docs
        coll = cx.pymongo_test.test_collection
        cursor = coll.find().sort([('_id', 1)])[0]
        yield cursor.fetch_next
        self.assertEqual({'_id': 0, 's': hex(0)}, cursor.next_object())

        yield AssertEqual(
            [{'_id': 5, 's': hex(5)}],
            coll.find().sort([('_id', 1)])[5].to_list)

        # Only 200 documents, so 1000th doc doesn't exist. PyMongo raises
        # IndexError here, but Motor simply returns None.
        cursor = coll.find()[1000]
        yield cursor.fetch_next
        self.assertEqual(None, cursor.next_object())
        yield AssertEqual([], coll.find()[1000].to_list)
        done()

    @async_test_engine()
    def test_cursor_index_each(self, done):
        cx = self.motor_client(host, port)

        # test_collection was filled out in setUp() with 200 docs
        coll = cx.pymongo_test.test_collection

        results = set()
        yield_points = []
        for i in range(3):
            yield_points.append((yield gen.Callback(i)))

        def each(result, error):
            if error:
                raise error

            if result:
                results.add(result['_id'])
            else:
                yield_points.pop()()

        coll.find({}, {'_id': 1}).sort([('_id', 1)])[0].each(each)
        coll.find({}, {'_id': 1}).sort([('_id', 1)])[5].each(each)

        # Only 200 documents, so 1000th doc doesn't exist. PyMongo raises
        # IndexError here, but Motor simply returns None, which won't show up
        # in results.
        coll.find()[1000].each(each)

        yield gen.WaitAll(list(range(3)))
        self.assertEqual(set([0, 5]), results)
        done()

    @async_test_engine()
    def test_rewind(self, done):
        cx = self.motor_client(host, port)
        cursor = cx.pymongo_test.test_collection.find().limit(2)

        count = 0
        while (yield cursor.fetch_next):
            cursor.next_object()
            count += 1
        self.assertEqual(2, count)

        cursor.rewind()
        count = 0
        while (yield cursor.fetch_next):
            cursor.next_object()
            count += 1
        self.assertEqual(2, count)

        cursor.rewind()
        count = 0
        while (yield cursor.fetch_next):
            cursor.next_object()
            break

        cursor.rewind()
        while (yield cursor.fetch_next):
            cursor.next_object()
            count += 1

        self.assertEqual(2, count)
        self.assertEqual(cursor, cursor.rewind())
        done()

    @gen.engine
    def wait_for_cursor(self, cursor, callback):
        """Wait 10 seconds for a cursor to be closed server-side, else fail
        """
        loop = ioloop.IOLoop.instance()
        patience_seconds = 10
        start = time.time()

        try:
            try:
                yield cursor.fetch_next
            except OperationFailure, e:
                # Let's check this error was because the cursor was killed, not a
                # test bug. mongod reports "cursor id 'N' not valid at server",
                # mongos says "database error: could not find cursor in cache for
                # id N over collection pymongo_test.test_collection".
                self.assertTrue(
                    "not valid at server" in e.args[0] or
                    "could not find cursor in cache" in e.args[0])
            else:
                now = time.time()
                if now - start > patience_seconds:
                    self.fail("Cursor not closed")
                else:
                    yield gen.Task(loop.add_timeout, time.time() + 1)

        except Exception, e:
            callback(None, e)
        else:
            callback(None, None)

    @async_test_engine()
    def test_del_on_main_greenlet(self, done):
        # Since __del__ can happen on any greenlet, MotorCursor must be
        # prepared to close itself correctly on main or a child.
        cx = self.motor_client(host, port)
        cursor = cx.pymongo_test.test_collection.find()
        yield cursor.fetch_next
        clone = cursor.clone()
        clone.delegate._Cursor__id = cursor.cursor_id

        # Clear the FetchNext reference from this gen.Runner so it's deleted
        # and decrefs the cursor
        yield gen.Task(ioloop.IOLoop.instance().add_callback)
        del cursor
        yield motor.Op(self.wait_for_cursor, clone)
        done()

    @async_test_engine()
    def test_del_on_child_greenlet(self, done):
        # Since __del__ can happen on any greenlet, MotorCursor must be
        # prepared to close itself correctly on main or a child.
        cx = self.motor_client(host, port)
        cursor = [cx.pymongo_test.test_collection.find()]
        yield cursor[0].fetch_next
        clone = cursor[0].clone()
        clone.delegate._Cursor__id = cursor[0].cursor_id

        # Clear the FetchNext reference from this gen.Runner so it's deleted
        # and decrefs the cursor
        yield gen.Task(ioloop.IOLoop.instance().add_callback)

        def f():
            # Last ref, should trigger __del__ immediately in CPython and
            # allow eventual __del__ in PyPy.
            del cursor[0]

        greenlet.greenlet(f).switch()
        yield motor.Op(self.wait_for_cursor, clone)
        done()


if __name__ == '__main__':
    unittest.main()
