# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/11/08
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest

import morph

#------------------------------------------------------------------------------
class TestMorph(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_isstr(self):
    self.assertTrue(morph.isstr(''))
    self.assertTrue(morph.isstr(u''))
    self.assertTrue(morph.isstr('abc'))
    self.assertTrue(morph.isstr(u'abc'))
    self.assertFalse(morph.isstr(['a', 'b', 'c']))
    self.assertFalse(morph.isstr(('a', 'b', 'c')))
    self.assertFalse(morph.isstr(list('abc')))
    self.assertFalse(morph.isstr(dict(abc='def')))
    self.assertFalse(morph.isstr(17))

  #----------------------------------------------------------------------------
  def test_isseq(self):
    self.assertTrue(morph.isseq(['a', 'b', 'c']))
    self.assertTrue(morph.isseq(('a', 'b', 'c')))
    self.assertTrue(morph.isseq(set(['a', 'b', 'c'])))
    class mylist(list): pass
    self.assertTrue(morph.isseq(mylist()))
    class myiter(object):
      def __iter__(self):
        return iter(['a', 'b', 'c'])
    self.assertTrue(morph.isseq(myiter()))
    self.assertFalse(morph.isseq('abc'))
    self.assertFalse(morph.isseq(u'abc'))
    class myobj(object): pass
    self.assertFalse(morph.isseq(myobj()))
    self.assertFalse(morph.isseq(dict(abc='def')))

  #----------------------------------------------------------------------------
  def test_isdict(self):
    self.assertTrue(morph.isdict(dict()))
    self.assertTrue(morph.isdict(dict(abc='def')))
    self.assertFalse(morph.isdict('abc'))
    self.assertFalse(morph.isdict(u'abc'))
    self.assertFalse(morph.isdict(['a', 'b', 'c']))

  #----------------------------------------------------------------------------
  def test_tobool(self):
    self.assertTrue(morph.tobool('true'))
    self.assertTrue(morph.tobool('TRUE'))
    self.assertFalse(morph.tobool('false'))
    self.assertFalse(morph.tobool('FALSE'))
    self.assertFalse(morph.tobool('nada'))
    with self.assertRaises(ValueError) as cm:
      morph.tobool('nada', default=None)
    self.assertTrue(morph.tobool(True))
    self.assertFalse(morph.tobool(False))

  #----------------------------------------------------------------------------
  def test_tolist(self):
    self.assertEqual(morph.tolist(['abc', 'def']), ['abc', 'def'])
    self.assertEqual(morph.tolist('abcdef'), ['abcdef'])
    self.assertEqual(morph.tolist('abc def'), ['abc', 'def'])
    self.assertEqual(morph.tolist('ab cd ef'), ['ab', 'cd', 'ef'])
    self.assertEqual(morph.tolist('"ab cd"\nef'), ['ab cd', 'ef'])

  #----------------------------------------------------------------------------
  def test_flatten(self):
    self.assertEqual(
      morph.flatten([1, [2, [3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}], 4]]),
      [1, 2, 3, 'abc', 'def', {'foo': ['zig', ['zag', 'zog']]}, 4])
    self.assertEqual(
      morph.flatten({'a': {'b': 'c'}}),
      {'a.b': 'c'})
    self.assertEqual(
      morph.flatten({'a': {'b': 1, 'c': [2, {'d': 3, 'e': 4}]}}),
      {'a.b': 1, 'a.c[0]': 2, 'a.c[1].d': 3, 'a.c[1].e': 4})
    self.assertEqual(
      morph.flatten({'a': {'b': [[1, 2], [3, {'x': 4, 'y': 5}, 6]]}}),
      {'a.b[0][0]':   1,
       'a.b[0][1]':   2,
       'a.b[1][0]':   3,
       'a.b[1][1].x': 4,
       'a.b[1][1].y': 5,
       'a.b[1][2]':   6,
       })

  #----------------------------------------------------------------------------
  def test_unflatten_fail(self):
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a.b': 'c', 'a[0]': 'no'})
    self.assertEqual(
      str(cm.exception),
      'conflicting structures (dict vs. list) for prefix: a')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a': 'b', 'a.b': 'c'})
    self.assertEqual(
      str(cm.exception),
      'conflicting scalar vs. structure for prefix: a')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a[0': 'b'})
    self.assertEqual(
      str(cm.exception),
      'invalid list syntax (no terminating "]") in key "a[0"')
    with self.assertRaises(ValueError) as cm:
      morph.unflatten({'a[NADA]': 'b'})
    self.assertEqual(
      str(cm.exception),
      'invalid list syntax (bad index) in key "a[NADA]"')

  #----------------------------------------------------------------------------
  def test_unflatten_ok(self):
    self.assertEqual(
      morph.unflatten({'a.b': 'c', 'd': 'e'}),
      {'a': {'b': 'c'}, 'd': 'e'})
    self.assertEqual(
      morph.unflatten({'a.b': 1, 'a.c[0]': 2, 'a.c[1]': 3, 'a.c[2]': 4}),
      {'a': {'b': 1, 'c': [2, 3, 4]}})
    self.assertEqual(
      morph.unflatten({'a.b': 1, 'a.c[0]': 2, 'a.c[1].d': 3, 'a.c[1].e': 4}),
      {'a': {'b': 1, 'c': [2, {'d': 3, 'e': 4}]}})
    self.assertEqual(
      morph.unflatten({
        'a.b[0][0]':   1,
        'a.b[0][1]':   2,
        'a.b[1][0]':   3,
        'a.b[1][1].x': 4,
        'a.b[1][1].y': 5,
        'a.b[1][2]':   6,
        }),
      {'a': {'b': [[1, 2], [3, {'x': 4, 'y': 5}, 6]]}})

  #----------------------------------------------------------------------------
  def test_pick(self):
    class aadict(dict): pass
    d = aadict(foo='bar', zig=87, ziggy=78)
    self.assertEqual(morph.pick(d, 'foo'), {'foo': 'bar'})
    self.assertEqual(morph.pick(d, 'foo', dict=aadict), {'foo': 'bar'})
    self.assertEqual(morph.pick(d), {})
    self.assertEqual(morph.pick(d, prefix='zi'), {'g': 87, 'ggy': 78})
    self.assertIsInstance(morph.pick(d, 'foo'), dict)
    self.assertNotIsInstance(morph.pick(d, 'foo'), aadict)
    self.assertIsInstance(morph.pick(d, 'foo', dict=aadict), aadict)
    self.assertEqual(morph.pick(d), {})

  #----------------------------------------------------------------------------
  def test_pick_object(self):
    class Thing(object):
      def __init__(self):
        self.foo = 'bar'
        self.zig1 = 'zog'
        self.zig2 = 'zug'
      def zigSomeMethod(self):
        pass
    src = Thing()
    self.assertEqual(
      morph.pick(src, 'foo', 'zig1'),
      {'zig1': 'zog', 'foo': 'bar'})
    self.assertEqual(
      morph.pick(src, prefix='zig'),
      {'1': 'zog', '2': 'zug'})
    self.assertEqual(morph.pick(src), {})

  #----------------------------------------------------------------------------
  def test_omit(self):
    class aadict(dict): pass
    d = aadict(foo='bar', zig=87, ziggy=78)
    self.assertEqual(morph.omit(d, 'foo'), {'zig': 87, 'ziggy': 78})
    self.assertEqual(morph.omit(d, prefix='zig'), {'foo': 'bar'})
    self.assertEqual(morph.omit(d), {'foo': 'bar', 'zig': 87, 'ziggy': 78})

  #----------------------------------------------------------------------------
  def test_omit_object(self):
    class Thing(object):
      def __init__(self):
        self.foo = 'bar'
        self.zig1 = 'zog'
        self.zig2 = 'zug'
      def zigSomeMethod(self):
        pass
    src = Thing()
    self.assertEqual(
      morph.omit(src, 'foo', 'zig1'),
      {'zig2': 'zug'})
    self.assertEqual(
      morph.omit(src, prefix='zig'),
      {'foo': 'bar'})
    self.assertEqual(
      morph.omit(src), {'foo': 'bar', 'zig1': 'zog', 'zig2': 'zug'})

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
