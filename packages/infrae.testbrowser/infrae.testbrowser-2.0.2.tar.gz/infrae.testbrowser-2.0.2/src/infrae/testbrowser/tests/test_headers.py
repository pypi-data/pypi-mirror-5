# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from infrae.testbrowser.headers import HTTPHeaders

class HeaderTestCase(unittest.TestCase):

    def test_set_and_get(self):
        """You can set and read values. This is case insensitive.
        """
        headers = HTTPHeaders()

        headers['content-type'] = 'text/plain'
        self.assertEquals(headers['content-type'], 'text/plain')
        self.assertEquals(headers['Content-Type'], 'text/plain')

        headers['Content-Type'] = 'application/octet-stream'
        self.assertEquals(headers['content-type'], 'application/octet-stream')
        self.assertEquals(headers['Content-Type'], 'application/octet-stream')

        headers.update(
            {'Content-Type': 'text/html', 'Content-Length': '42'}.items())
        self.assertEquals(headers['content-type'], 'text/html')
        self.assertEquals(headers['content-length'], '42')

    def test_non_existing_get(self):
        """Looking a non existing key raises KeyError.
        """
        headers = HTTPHeaders()

        self.assertRaises(KeyError, headers.__getitem__, 'Missing')
        self.assertRaises(KeyError, headers.__getitem__, 'missing')

    def test_has_key(self):
        """You can check is an header is already set. This is case
        insensitive as well.
        """
        headers = HTTPHeaders()

        headers['Content-Length'] = '42'
        self.assertEquals(headers.has_key('Content-Length'), True)
        self.assertEquals(headers.has_key('content-length'), True)
        self.failUnless('Content-Length' in headers)
        self.failUnless('content-length' in headers)

        self.assertEquals(headers.has_key('Server'), False)
        self.assertEquals(headers.has_key('server'), False)
        self.failIf('Server' in headers)
        self.failIf('server' in headers)

    def test_items(self):
        """items return a list of tuples containing all headers. Header
        names are normalized, and value are converted to strings.
        """
        headers = HTTPHeaders()

        headers['content-type'] = 'text/plain'
        headers['Content-length'] = 42
        self.assertEquals(
            headers.items(),
            [('Content-Length', '42'), ('Content-Type', 'text/plain')])
        self.assertEquals(
            list(headers.iteritems()),
            [('Content-Length', '42'), ('Content-Type', 'text/plain')])

