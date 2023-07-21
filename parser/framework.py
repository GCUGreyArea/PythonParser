#!/usr/bin/env python3

import sys
import os
import re
from rules import get_rules,build_partitions 
from kv_py_parse import KVParser


# An action can either map to a token name 
# or require that the fragment to with the 
# action belongs to be reparsed.
# 
# In the case of a token the action will contain
# the name of token the fragment should be expressed 
# as. 
# 
# In the case of forwarding the action will contain 
# the name and type of the partition that the 
# fragment should be forwarded to as a string in the 
# form name:type.
# 
# A flag will tell the Framework which type of action 
# this is.

class Action:
    def __init__(self, string,flag):
        self._string = string
        self._map = flag

    def is_map(self):
        return self._map
    
    def string(self):
        return self._string
    
    def to_string(self):
        m = None
        if self._map:
            m = 'map'
        else:
            m = 'forward'
        
        return self._string + ' => ' + m  

# Each engine contains all the patterns for that type in the partition
# there can be multiple engine types in the same partition but all 
# patterns for that type in that partition will reside with that one engine.

class Engine:
    def __init__(self,type):
        self._type = type
        self._patterns = []

    def add_pattern(self,ptn):
        if ptn.type() != self._type:
            raise ValueError(f"Pattern has the wrong type: {ptn.type()}")
        
        self._patterns.append(ptn)

    def print(self):
        print("type: ",self._type)
        for p in self._patterns:
            p.print()

# Engine for regex parsing
class RegexEngine(Engine):
    def __init__(self):
        super().__init__('regex')
        self._reg = []

    def print(self):
        super().print()

    def finalise(self):
        for p in self._patterns:
            triggers = p.triggers()
            maps = p.map()

            action_map = {}
            if triggers is not None:
                for t in triggers:
                    name = t['name']
                    format = t['format']
                    partition = t['partition']
                    action_map[name] = Action(partition + ':' + format, False)

            if maps is not None:
                for label,path in maps.items():
                    action_map[label] = Action(path, True)

            # Add this is a tuple
            self._reg.append( (re.compile(p.pattern()),action_map) )

    def parse(self,frag_str):
        FrgList = []
        for ptn,act_map in self._reg:
            m = ptn.match(frag_str)
            if m:
                for n,i in ptn.groupindex.items():
                    val = m.group(i)
                    action = act_map[n]
                    FrgList.append((val,action))
                
                return FrgList
            
        return FrgList


# engine for kv parsing
class KvEngine(Engine):
    def __init__(self, KSep = '=', VSep = ','):
        super().__init__('kv')
        self._parser = KVParser('',KSep,VSep)
        print("made kv engine")

    def parse(self,string):
        KeyMap = self._parser.set(string)

        # 'match': {'.ocupation': 'Lead Cyber Engineer', '.roles.skils[]': {'contains': 'java'}, '.productivity': None
        for Ptn in self._patterns:
            Match = Ptn.match()

    def print(self):
        super().print()

    def finalise(self):
        pass

# engine for json parsing
class JsonEngine(Engine):
    def __init__(self):
        super().__init__('json')

    def print(self):
        super().print()

    def finalise(self):
        pass

# Framework class to run parsers
class Framework: 
    def __init__(self, rule_dir):
        # Find all flies that end in "yaml" and who's names are a mix of letters and numbers
        Files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(rule_dir)) for f in fn if re.match(r'[\w\d]+\.yaml', f)]
        self._partitions = {}
        self._rule_list = []
        for File in Files:
            RuleList = get_rules(File)
            self._rule_list.append(RuleList)
            Partition = build_partitions(RuleList)
            self._partitions.update(Partition)

        self._engines = self._build_parsing_engines()

    def _build_parsing_engines(self):
        engines = {}
        for PartName,PartList in self._partitions.items():
            for Ptn in PartList:
                type = Ptn.type()
                name = PartName + ':' + type
                try:
                    eng = engines[name]
                except KeyError:
                    if type == 'regex':
                        eng = RegexEngine()
                    elif type == 'kv':
                        eng = KvEngine()
                    elif type == 'json':
                        eng = JsonEngine()
                    else:
                        raise ValueError(f"Unnkonw engine type : {type}")
                finally:
                    engines[name] = eng

                eng.add_pattern(Ptn)

        for _,e in engines.items():
            e.finalise()

        return engines

    def parse_fragment(self,FragStr,partition):
        try:
            eng = self._engines[partition]
        except KeyError:
            raise ValueError(f"Ilegal partition name {partition} sent to parse_fragment")
        
        frags = eng.parse(FragStr)

        tokens = {}
        for frag,action in frags:
            if action.is_map():
                tokens[action.string()] = frag
            else:
                res = self.parse_fragment(frag,action.string())
                tokens.update(res)

        return tokens

    def print(self):
        print("engines:")
        for _,eng in self._engines.items():
            eng.print()

def main(dir, message):
        f = Framework(dir)

        res = f.parse_fragment(message, 'root:regex')
        print('tokens: ',res)

if __name__ == '__main__':
    if len(sys.argv) != 3: 
        print('usage: ./framework.py <rule dir> <message>')
        print('rule dir: The root directory for rules files')
        print('message: The message to parse using the rules')
    else: 
        main(sys.argv[1],sys.argv[2])