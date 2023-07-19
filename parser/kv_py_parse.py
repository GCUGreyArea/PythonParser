#!/usr/bin/env python3

import sys

class SpanErr(Exception):
    pass

# A place to save each word as a span
class Span: 
    def __init__(self,start,end):
        self._start = start
        self._end = end
        if(self._start > self._end):
            raise SpanErr("start of span goes past end of span")


    def set(self,start,end):
        self._start = start
        self._end = end
        if(self._start > self._end):
            raise SpanErr("start of span goes past end of span")

    
    def get_end(self):
        return self._end
    
    
    def set_end(self,end):
        self._end = end


    def get_start(self):
        return self._start


    def set_start(self,start):
        self._start = start
        if(self._start > self._end):
            raise SpanErr("start of span goes past end of span")

    def from_string(self,string):
        return string[self._start:self._end]
    

    def print(self):
        print(self._start,":",self._end)

    
    def add_start(self,amount):
        self._start += amount
        if(self._start > self._end):
            raise SpanErr("start of span goes past end of span")


    def inc_start(self):
        self._start += 1
        if(self._start > self._end):
            raise SpanErr("start of span goes past end of span")
        
    
    def slide_start_and_end(self):
        self._start +=1
        self._end +=1


    def inc_end(self):
        self._end +=1

class KVParser:
    def __init__(self, string, ksep = '=', vsep = ','):
        self._ksep = ksep
        self._vsep = vsep
        self._string = string
        self._len = len(string)
        self._keys = []
        self._values = []
        self._KV = {}   
        self._span = Span(0,0) # currnt word in parsing


    def string(self):
        return self._string
    

    def set(self,string, ksep = '=', vsep = ','):
        self._ksep = ksep
        self._vsep = vsep
        self._string = string
        self._len = len(string)
        self._keys = []
        self._values = []
        self._KV = {}   
        self._span.set(0,0)

    
    def len(self):
        return self._len

    def keys(self):
        return self._keys
    
    def values(self):
        return self._values

    # eat up spaces and KV seperators
    def eat_up_garbage(self):
        if self._span.get_end() == self.len():
            return()
        
        place = self._span.get_start()
        
        while self._string[place] == ' ':
            place += 1

        if place != self._span.get_start():
            self._span.add_start(place)

        if self._string[place] == self._ksep or self._string[place] == self._vsep:
            self._span.slide_start_and_end()
            while self._string[self._span.get_start()] == ' ':
                self._span.slide_start_and_end()


    def do_value(self):
        self.eat_up_garbage()
        self._span.set_end(self._span.get_start())

        for Chr in self._string[self._span.get_start():self._len]:
            if Chr != self._vsep:
                self._span.inc_end()
            elif Chr == self._vsep:
                break
            elif Chr == self._ksep:
                raise ValueError("invalid input: ", self._string)

        # Catch end of string for last vale
        self._values.append(Span(self._span.get_start(),self._span.get_end()))

        self._span.set_start(self._span.get_end())
            

    def do_key(self):
        self.eat_up_garbage()
        self._span.set_end(self._span.get_start())
        for Chr in self._string[self._span.get_start():self._len]:
            if Chr != self._ksep:
                self._span.inc_end()
            elif Chr == self._ksep:
                self._keys.append(Span(self._span.get_start(),self._span.get_end()))
                break
            elif Chr == self._vsep:
                raise ValueError("invalid input: ", self._string)
        
        self._span.set_start(self._span.get_end())  

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
        while self._span.get_end() != self._len:
            self.do_key()
            self.do_value()

        if len(self._keys) != len(self._values):
            print("ERROR: Key value mismatch")
            return()
        
        for Cnt in range(len(self._keys)):
            Key = self._keys[Cnt].from_string(self._string)
            Value = self._values[Cnt].from_string(self._string)
            self.decode_and_apply_entry(self._KV,Key.strip(),Value.strip()) 

        self._span = Span(0,0)


    def print(self):
        for key,value in self._KV.items():
            print(key,'=>',value)


    def reset(self,String):
        self._span = Span(0,0)
        self._string = String
        self._len = len(String)
        self._KV.clear()
        self._values.clear()
        self._keys.clear()


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
    P1 = KVParser(String)
    P1.run_parser()
    P1.print()
    String = "target=Moriarty, detective=Holms, assistant=Watson"
    P1.set(String)
    P1.run_parser()
    P1.print()

    String = "satisfaction&good# name&Barry Robinson # employer&Northrup Grumman # aspiration & principal engineer"
    P2 = KVParser(String,'&','#')
    P2.run_parser()
    P2.print()


def tst(): 
    test_span() 
    test_parsers()


def main(KV, KS = '=', VS = ','): 
    P1 = KVParser(KV, KS, VS)
    P1.run_parser()
    P1.print()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('please supply a KV string and optionally key and value sperators')
    elif len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1])
