#!/usr/bin/env python3

import sys
import os
import re
from rules import get_rules,build_partitions 
from kv_py_parse import KVParser
import json


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
        self._patterns = {}

    def add_pattern(self,ptn):
        if ptn.type() != self._type:
            raise ValueError(f"Pattern has the wrong type: {ptn.type()}")
        
        self._patterns[ptn.uuid()] = ptn

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
        for _,p in self._patterns.items():
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
            self._reg.append( (re.compile(p.pattern()),action_map,p) )

    def parse(self,frag_str):
        FrgList = []
        Ret = (None,FrgList)
        for ptn,act_map,p in self._reg:
            m = ptn.match(frag_str)
            if m:
                for n,i in ptn.groupindex.items():
                    val = m.group(i)
                    action = act_map[n]
                    FrgList.append((val,action))
                

                return (p,FrgList)
            
        return Ret


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
        self._rule_by_id = {}
        self._rule_by_pattern_id = {} 
        for File in Files:
            RuleList = get_rules(File)
            for Rule in RuleList:
                self._rule_by_id[Rule.uuid()] = Rule

            self._build_rule_by_pattern_id(RuleList)
    
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


    def _build_rule_by_pattern_id(self,RuleList):
        RuleMap = {}
        for Rule in RuleList:
            PtnList = Rule.patterns()
            for Ptn in PtnList:
                RuleMap[Ptn.uuid()] = Rule
        
        self._rule_by_pattern_id.update(RuleMap)


    def parse_fragment(self,FragStr,partition):
        try:
            eng = self._engines[partition]
        except KeyError:
            raise ValueError(f"Ilegal partition name {partition} sent to parse_fragment")
        
        (Ptn,FragList) = eng.parse(FragStr)

        if Ptn is None and len(FragList) == 0:
            return None

        tokens = {}
        ptnList = []
        ptnList.append(Ptn.uuid())
        for frag,action in FragList:
            if action.is_map():
                tokens[action.string()] = frag
            else:
                Ret = self.parse_fragment(frag,action.string())
                if Ret is None:
                    break
                (PtnList,res) = Ret
                for p in PtnList:
                    ptnList.append(p)
                tokens.update(res)

        return (ptnList,tokens)

    def print(self):
        print("engines:")
        for _,eng in self._engines.items():
            eng.print()


    def generate_output(self,UuidList,parse_map):
        RuleMap = {}
        RuleList = []
        for uuid in UuidList:
            R = self._rule_by_pattern_id[uuid]
            Ruuid = R.uuid()
            try:
                RuleMap[Ruuid]
            except KeyError:
                RuleMap[Ruuid] = Ruuid
                RuleList.append(Ruuid)

        out = {}
        if len(RuleList) == 0: 
            pass
        elif len(RuleList) == 1:
            out['rule'] = RuleList[0]
        else:
            out['rule'] = RuleList

        out['pattern'] = UuidList
        out['tokens'] = parse_map

        return out
        

def main(dir, message):
        f = Framework(dir)
        (PtnList,Token) = f.parse_fragment(message, 'root:regex')
        out = f.generate_output(PtnList,Token)
        print(json.dumps(out))

if __name__ == '__main__':
    if len(sys.argv) != 3: 
        print('usage: ./framework.py <rule dir> <message>')
        print('rule dir: The root directory for rules files')
        print('message: The message to parse using the rules')
    else: 
        main(sys.argv[1],sys.argv[2])