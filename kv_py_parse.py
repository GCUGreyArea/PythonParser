#!/usr/bin/env python3

import sys

# A place to save each word as a span
class Span: 
    Start = 0
    End = 0
    def __init__(self,Start,End):
        self.Start = Start
        self.End = End

    def from_string(self,String):
        St = String[self.Start:self.End]
        return St
    
    def print(self):
        print(self.Start,":",self.End)
    

class KVBase:
    # Key and Value seperators
    KSep = '='
    VSep = ','

    # Variables
    String = ''

    # lists of Spans in the String 
    # that represent words which are keys 
    # or values
    Keys = []
    Values = []
    Len = 0      # Length of the string
    Span = Span(0,0) # currnt word in parsing

    # The dict object we will construct
    KV = {}

    def __init__(self, String):
        self.String = String
        self.Len = len(String)
        self.Keys = []
        self.Values = []
        self.KV = {}
        self.Span = Span(0,0) # currnt word in parsing


    # eat up spaces and KV seperators
    def eat_up_garbage(self):
        if self.Span.End == self.Len:
            return()
        
        Place = self.Span.Start
        
        while self.String[Place] == ' ':
            Place += 1

        if Place != self.Span.Start:
            self.Span.Start += Place

        if self.String[Place] == self.KSep or self.String[Place] == self.VSep:
            self.Span.Start += 1
            while self.String[self.Span.Start] == ' ':
                self.Span.Start += 1


    def do_value(self):
        self.eat_up_garbage()
        self.Span.End = self.Span.Start

        for Chr in self.String[self.Span.Start:self.Len]:
            if Chr != self.VSep:
                self.Span.End += 1
            elif Chr == self.VSep:
                break
            elif Chr == self.KSep:
                return -1

        # Catch end of string for last vale
        self.Values.append(Span(self.Span.Start,self.Span.End))

        self.Span.Start = self.Span.End
        return self.Span.End
            

    def do_key(self):
        self.eat_up_garbage()
        self.Span.End = self.Span.Start
        for Chr in self.String[self.Span.Start:self.Len]:
            if Chr != self.KSep:
                self.Span.End += 1
            elif Chr == self.KSep:
                self.Keys.append(Span(self.Span.Start,self.Span.End))
                break
            elif Chr == self.VSep:
                return -1
        
        self.Span.Start = self.Span.End  
        return self.Span.End

    def is_float(self, Str):
        try: 
            float(Str)
            return True
        except ValueError:
            return False

    def decode_and_apply_entry(self,Dict,Key,Value):
        K = None
        V = None
        if Key.isnumeric():
            K = int(Key)
        elif self.is_float(Key): 
            K = float(Key)
        else:
            K = Key

        if Value.isnumeric():
            V = int(Value)
        elif self.is_float(Value):
            V = float(Value)
        else: 
            V = Value

        Dict[K] = V


    def run_parser(self):
        while self.Span.End != self.Len:
            self.do_key()
            self.do_value()

        if len(self.Keys) != len(self.Values):
            print("ERROR: Key value mismatch")
            return()
        
        for Cnt in range(len(self.Keys)):
            Key = self.Keys[Cnt].from_string(self.String)
            Value = self.Values[Cnt].from_string(self.String)
            self.decode_and_apply_entry(self.KV,Key.strip(),Value.strip()) 

        self.Span = Span(0,0)


    def print(self):
        print(self.KV)


    def reset(self,String):
        self.Span = Span(0,0)
        self.String = String
        self.Len = len(String)
        self.KV.clear()
        self.Values.clear()
        self.Keys.clear()
           

class KVDefault(KVBase):
    def __init__(self,Str):
        super(KVDefault,self).__init__(Str)
   

class KVSep(KVBase):
    def __init__(self,Str,KSep = '=', VSep = ','):
        super(KVSep,self).__init__(Str)
        self.KSep = KSep
        self.VSep = VSep


def test_span():
    sp = Span(5,10)
    str = 'this world'
    print(sp.from_string(str))

    List = []

    List.append(Span(1,2))
    List.append(Span(3,4))
    List.append(Span(5,6))

    for X in List:
        X.print()


def test_parsers():
    # Test the parsers
    String = "satisfaction=good, name = Barry Robinson, employer=Northrup Grumman, aspiration = principal engineer"
    P1 = KVSep(String)
    P1.run_parser()
    P1.print()
    String = "target=Moriarty, detective=Holms, assistant=Watson"
    P1.reset(String)
    P1.run_parser()
    P1.print()

    String = "satisfaction&good# name&Barry Robinson # employer&Northrup Grumman # aspiration & principal engineer"
    P2 = KVSep(String,'&','#')
    P2.run_parser()
    P2.print()


def tst(): 
    test_span() 
    test_parsers()


def main(KV, KS = '=', VS = ','): 
    P1 = KVSep(KV, KS, VS)
    P1.run_parser()
    P1.print()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('please supply a KV string and optionally key and value sperators')
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1])
