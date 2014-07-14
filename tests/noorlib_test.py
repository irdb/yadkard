#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Test noorlib.py module."""


import unittest
import sys

import dummy_requests
sys.path.append('..')
import noorlib


class NoorlibTest(unittest.TestCase):

    def test_nl1(self):
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18879'
        o = noorlib.Response(i)
        e = '* {{cite book|last=مرتضی زبیدی|first=محمد بن محمد|last2=شیری|first2=علی|title=تاج العروس من جواهر القاموس|publisher=دار الفکر|location=بيروت|series=تاج العروس من جواهر القاموس|volume=10|url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18879|language=عربی|ref=harv|accessdate='
        self.assertIn(e, o.ctnt)

    def test_nl2(self):
        """The year parameter is not present."""
        i = 'http://www.noorlib.ir/View/fa/Book/BookView/Image/18454'
        o = noorlib.Response(i)
        er = '{{sfn|کورانی}}'
        ec = '* {{cite book|last=کورانی|first=علی|title=المعجم الموضوعی لاحادیث الامام المهدی عجل الله تعالی فرجه الشریف|publisher=دار المرتضی|location=بيروت|series=المعجم الموضوعی لاحادیث الامام المهدی عجل الله تعالی فرجه الشریف|volume=1|url=http://www.noorlib.ir/View/fa/Book/BookView/Image/18454|language=عربی|ref=harv|accessdate='
        self.assertIn(er, o.sfnt)
        self.assertIn(ec, o.ctnt)


noorlib.requests = dummy_requests.DummyRequests()
if __name__ == '__main__':
    unittest.main()