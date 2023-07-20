#!/usr/bin/env python3

import os
import unittest
import re
from kv_py_parse import KVParser
from json_py_parse import parse_json,contains
from rules import uuidStore,get_rules


# Fix issue with test runner in vscode by 
# the passing complete path
def setup_cwd():
    cwd = os.getcwd()
    if(cwd == "/home/barry/python_course/Fundamentals"):
        cwd +='/parser/'
    else:
        cwd += '/'

    return cwd
 

"""Test thatthe parsers function correctly."""
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


    def test_uuid_store(self):
        # There can only ne one of each uuid
        uuid = '3a7cc24a-b0f9-41da-812b-01b3ab675b41'
        self.assertTrue(uuidStore.validate(uuid))
        self.assertFalse(uuidStore.validate(uuid))

        # uuid is too short
        uuid = '6b762f3c-8210-4def-8443-a8e0a8efe5'
        self.assertFalse(uuidStore.validate(uuid))

    def test_yaml_decoder_exceptions(self):
        cwd = setup_cwd()
        try:
            get_rules(cwd + 'resources/test_rule_one.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Pattern cdde2e49-dc42-40be-bfae-1baa3c4583fa does not have a name")

        try:
            get_rules(cwd + 'resources/test_rule_two.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Pattern cdde2e49-dc42-40be-bfae-1baa3c4583fa does not have a type")

        try:
            get_rules(cwd + 'resources/test_rule_three.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Pattern cdde2e49-dc42-40be-bfae-1baa3c4583fa does not declare a partition")
            
        try:
            get_rules(cwd + 'resources/test_rule_four.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Pattern cdde2e49-dc42-40be-bfae-1baa3c4583fa does not have a pattern entry")

        try:
            get_rules(cwd + 'resources/test_rule_five.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Pattern cdde2e49-dc42-40be-bfae-1baa3c4583fa must have a triggers entry or map to tokens")
        
        try:
            get_rules(cwd + 'resources/test_rule_six.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Rule e9e50fbc-f4bc-480b-b168-f1279ba559c2 in file /home/barry/python_course/Fundamentals/parser/resources/test_rule_six.yaml has no name")

        try:
            get_rules(cwd + 'resources/test_rule_seven.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Rule in file /home/barry/python_course/Fundamentals/parser/resources/test_rule_seven.yaml has no id")

        try:
            get_rules(cwd + 'resources/test_rule_eight.yaml')
        except ValueError as e:
            self.assertEqual(str(e),"Rule e9e50fbc-f4bc-480b-b168-f1279ba559c2 in file /home/barry/python_course/Fundamentals/parser/resources/test_rule_eight.yaml has no patterns")

    def test_rule_list(self):
        cwd = setup_cwd()

        RList = get_rules(cwd + 'resources/test_rule_nine.yaml')
        self.assertTrue(len(RList) == 2)

        R1 = RList[0]

        self.assertEqual(R1.uuid(),'e9e50fbc-f4bc-480b-b168-f1279ba559c2')
        self.assertEqual(R1.name(),'test rule one')

        R2 = RList[1]

        self.assertEqual(R2.uuid(),'898cfde0-70a3-407a-ac3c-251f5946a973')
        self.assertEqual(R2.name(),'test rule two')

        P1 = R1.patterns()

        self.assertEqual(P1[0].uuid(),'cdde2e49-dc42-40be-bfae-1baa3c4583fa')
        self.assertEqual(P1[0].name(),'aws json one')
        self.assertEqual(P1[0].type(),'regex')
        self.assertEqual(P1[0].partition(),'root')
        self.assertEqual(P1[0].pattern(),'^aws: (?P<json>{.*})')

        self.assertEqual(P1[1].uuid(),'0b1db7a5-0308-4bfb-87e3-b2a48cee6b88')
        self.assertEqual(P1[1].name(),'basic kv one')
        self.assertEqual(P1[1].type(),'regex')
        self.assertEqual(P1[1].partition(),'root')
        self.assertEqual(P1[1].pattern(),'^(?P<kv>[\d\w ]+=[\d\w ]+,*(?:[\d\w ]+=[\d\w ]+)*,[\d\w ]+=[\d\w ]+)')

        P2 = R2.patterns()
        self.assertEqual(P2[0].uuid(),'4552667a-12c6-46c1-ac10-f949e0633f9a')
        self.assertEqual(P2[0].name(),'aws json two')


        self.assertEqual(P2[1].uuid(),'4a06182f-2abe-475d-a7d6-d071bd4377d0')
        self.assertEqual(P2[1].name(),'basic kv two')

if __name__ == '__main__':
    unittest.main()