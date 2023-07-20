#!/usr/bin/env python3

import sys
import yaml
import os
import re

class DuplicateUUID(Exception):
    pass

class GlobalUuid:
    _map = {}

    def _valid_uuid(self,uuid):
        Reg = r"^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$"
        if not re.match(Reg,uuid):
            return False
        
        return True

    def validate(self,uuid):
        try:
            self._map[uuid]
        except KeyError:
            self._map[uuid] = True
            return self._valid_uuid(uuid)

        return False

# Single instance of the uuid store. This needs to deduplicate UUIDs and 
# is used to raise an exception if the UUID does not validate
uuidStore = GlobalUuid()
class Pattern:
    def __init__(self,uuid,ptn,type,name,triggers,mappings,partition):
        if not uuidStore.validate(uuid):
            raise ValueError(f"uuid is invalid: {uuid}")
        self._uuid = uuid
        self._ptn = ptn
        self._type = type
        self._name = name
        self._triggers = triggers
        self._mappings = mappings
        self._partition = partition

    def uuid(self):
        return self._uuid

    def pattern(self):
        return self._ptn
    
    def type(self):
        return self._type
    
    def name(self):
        return self._name

    def triggers(self):
        return self._triggers
    
    def mappings(self):
        return self._mappings
    
    def partition(self):
        return self._partition
    
    def print(self):
        print('\tname: ',self._name,
              '\tuuid: ',self._uuid,
              '\ttype: ',self._type,
              '\tpartition: ',self._partition,
              '\tpattern: ', self._ptn)
    
class Rule:
    def __init__(self,uuid,name, patterns):
        if not uuidStore.validate(uuid):
            raise ValueError(f"uuid is invalid: {uuid}")
        
        self._uuid = uuid
        self._name = name
        self._patterns = patterns

    def uuid(self):
        return self._uuid
    
    def name(self):
        return self._name
    
    def patterns(self):
        return self._patterns
    

    def print(self):
        print('uuid: ',self._uuid)
        print('name: ',self._name)
        print('patterns: ')
        for ptn in self._patterns:
            ptn.print()

def load_yaml(FName):
    f = open(FName)
    Y = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return Y


def _get_rule_patterns(Ptns):
    Trigs = []
    Maps = []
    uuid = None
    ptn = None
    name = None
    type = None
    partition = None

    Patterns = []
    for P in Ptns:
        try:
            uuid = P['id']
        except KeyError:
            raise ValueError(f"Pattern {P}  does not have an id")
        
        # We must have at least one of either triggers or mappings
        try:
            Trigs = P['triggers']
        except KeyError:
            pass
        try: 
            Maps = P['mappings']
        except KeyError:
            pass
        if len(Trigs) == 0 and len(Maps) == 0:
            raise ValueError(f'Pattern {uuid} must have a triggers entry or map to tokens')
        
        try: 
            ptn = P['pattern']
        except KeyError:
            raise ValueError(f"Pattern {uuid} does not have a pattern entry")
        
        try: 
            type = P['type']
        except KeyError:
            raise ValueError(f"Pattern {uuid} does not have a type") 
        
        try: 
            name = P['name']
        except KeyError:
            raise ValueError(f"Pattern {uuid} does not have a name")
        
        try:
            partition = P['partition']
        except KeyError:
            raise ValueError(f"Pattern {uuid} does not declare a partition")
        Patterns.append(Pattern(uuid,ptn,type,name,Trigs,Maps,partition))

    return Patterns


def get_rules(FName):
    """
        Get the patters from a YAML file and validate that entries are correct
        Args: 
            path to a valid YAML rules file

        Returns: 
            A list of filled out Rule object

        Exceptions: 
            VaueError: Thrown when a yaml rule file contains a bad entry
    """
    YamlRules = load_yaml(FName)

    ParsedRules = []
    
    for YamlRule in YamlRules:
        Patterns = []
        ID = None
        Name = None
        Ptns = None

        try: 
            ID = YamlRule['id']
        except KeyError:
            raise ValueError(f"Rule in file {FName} has no id")
        
        try: 
            Name = YamlRule['name']
        except KeyError:
            raise ValueError(f"Rule {ID} in file {FName} has no name")
        
        try:
            Ptns = YamlRule['patterns']
        except KeyError:
            raise ValueError(f"Rule {ID} in file {FName} has no patterns")

        Patterns = _get_rule_patterns(Ptns)
        ParsedRules.append(Rule(ID,Name,Patterns))
    
    return ParsedRules


def build_partitions(Rules):
    Partitions = {}
    for Rule in Rules:
        for Ptn in Rule.patterns():
            PtnList = []
            try:
                PtnList = Partitions[Ptn.partition()]
            except KeyError:
                Partitions[Ptn.partition()] = PtnList
                
            PtnList.append(Ptn)

    return Partitions

def main(file):
    Rules = get_rules(file)

    # set up patterns by partition
    Partitions = build_partitions(Rules)

    print("==> Partitions:")
    for Name,Part in Partitions.items():
        print("Name: ",Name)
        for P in Part:
            P.print()

    print("==> Rules:")
    for Rule in Rules:
        Rule.print()

if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print('please supply a file to parse')
    else: 
        main(sys.argv[1])