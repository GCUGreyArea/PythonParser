#!/usr/bin/env python3

import unittest
import re
from kv_py_parse import KVParser
from json_py_parse import parse_json,contains

"""Test that regex for detection gives 
   the correct output
"""
class TestParsersAndRegex(unittest.TestCase):
    def test_json_regex(self):
        Re = '^aws: (?P<json>{.*})'
        St = 'aws: {"name":"Barry Robinson","ocupation":"LEad cyber engineer"}'
        Match = re.search(Re, St)
        json = Match.group('json')
        self.assertEqual(json,'{"name":"Barry Robinson","ocupation":"LEad cyber engineer"}')

    def test_kv_regex(self):
        Re = '^(?P<kv>[\d\w ]+=[\d\w ]+,*(?:[\d\w ]+=[\d\w ]+)*,[\d\w ]+=[\d\w ]+)'
        St = 'name = Barry Robinson, ocupation = Lead Cyber Egineer'
        Match = re.search(Re,St)
        kv = Match.group('kv')
        self.assertEqual(kv,St)

    def test_kv_parser(self):
        St = 'name = Barry Robinson, ocupation = Lead Cyber Engineer'
        P = KVParser(St)
        KVMap = P.run_parser()
        self.assertEqual(KVMap['.name'],'Barry Robinson')
        self.assertEqual(KVMap['.ocupation'],'Lead Cyber Engineer')

    def test_json_parser(self):
        St = '{"name":"Barry Robinson","skils": {"current":["c++","Java","c"],"future":["python","AWS"]}}'
        Map = parse_json(St)
        self.assertEqual(Map['.name'],'Barry Robinson')
        self.assertEqual(Map['.skils.current[0]'],'c++')
        self.assertEqual(Map['.skils.current[1]'],'Java')
        self.assertEqual(Map['.skils.current[2]'],'c')
        self.assertEqual(Map['.skils.future[0]'],'python')
        self.assertEqual(Map['.skils.future[1]'],'AWS')
        self.assertTrue(contains(Map,'.skils.future[]','python'))
        self.assertTrue(contains(Map,'.skils.future[]','AWS'))
        self.assertTrue(contains(Map,'.skils.current[]','Java'))
        self.assertTrue(contains(Map,'.skils.current[]','c'))
        self.assertTrue(contains(Map,'.skils.current[]','c++'))

if __name__ == '__main__':
    unittest.main()