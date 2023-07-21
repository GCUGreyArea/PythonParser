#!/usr/bin/env python3

import os
import unittest
import re
from kv_py_parse import KVParser
from json_py_parse import parse_json,contains
from rules import uuidStore,get_rules
from framework import Framework


# Fix issue with test runner in vscode by 
# the passing complete path
def _setup_cwd():
    cwd = os.getcwd()
    if(cwd[-12:] == "Fundamentals"):
        cwd +='/parser/'
    else:
        cwd += '/'

    return cwd
 
cwd = _setup_cwd()

def get_file_path(file,test):
    return cwd + 'resources/' + test + '/' + file

# Test that the parsers function correctly.
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
        try:
            file = get_file_path('test_rule_one.yaml', 'assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),"Pattern 958ca0c5-df83-4267-b873-4f34fad95fbf does not have a name")

        try:
            file = get_file_path('test_rule_two.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),"Pattern has no type: {'id': 'f9108c6b-a924-4dbc-a0df-583593e1bb5b', 'name': 'aws json', 'partition': 'root', 'pattern': '^aws: (?P<json>{.*})', 'triggers': [{'name': 'json', 'action': 'forward', 'format': 'json', 'partition': 'aws json'}]}")

        try:
            file = get_file_path('test_rule_three.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),"Pattern 5ceaf8a7-8551-4dd7-aeeb-2c0ec482c8c3 does not declare a partition")
            
        try:
            file = get_file_path('test_rule_four.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),"Pattern 00d4c181-6105-49cd-8bd6-dd7006212e43 does not have a pattern entry")

        try:
            file = get_file_path('test_rule_five.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual("A regex pattern must have at least one triggers or map statement",str(e))
        
        try:
            file = get_file_path('test_rule_six.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            file = get_file_path('test_rule_six.yaml','assertions')
            self.assertEqual(f"Rule e9e50fbc-f4bc-480b-b168-f1279ba559c2 in file {file} has no name",str(e))

        try:
            file = get_file_path('test_rule_seven.yaml','assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),f"Rule in file {file} has no id")

        try:
            file = get_file_path("test_rule_eight.yaml",'assertions')
            get_rules(file)
        except ValueError as e:
            self.assertEqual(str(e),f"Rule e9e50fbc-f4bc-480b-b168-f1279ba559c2 in file {file} has no patterns")

    def test_rule_list(self):
        file = get_file_path("test_rule_nine.yaml",'assertions')
        RList = get_rules(file)
        self.assertTrue(len(RList) == 2)

        R1 = RList[0]

        self.assertEqual(R1.uuid(),'e9e50fbc-f4bc-480b-b168-f1279ba559c2')
        self.assertEqual(R1.name(),'test rule one')

        R2 = RList[1]

        self.assertEqual(R2.uuid(),'898cfde0-70a3-407a-ac3c-251f5946a973')
        self.assertEqual(R2.name(),'test rule two')

        P1 = R1.patterns()

        self.assertEqual(P1[0].uuid(),'0248953f-7d46-42ea-af3d-4ce067075eff')
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

    # That the framework returns a list of fragments
    # for a parsed message
    def test_framework_one(self):
        path = get_file_path('','framework_one')
        f = Framework(path)

        res = f.parse_fragment('name: barry age: 58', 'root:regex')

        self.assertEqual('barry',res['name'])
        self.assertEqual('58',res['age'])

    def test_framework_two(self):
        path = get_file_path('','framework_two')
        f = Framework(path)

        res = f.parse_fragment('aws: {"name":"Barry Robinson","value":"high"}', 'root:regex')

        self.assertEqual('Barry Robinson',res['name'])
        self.assertEqual('high',res['value'])

if __name__ == '__main__':
    unittest.main()