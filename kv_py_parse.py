
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

    def run_parser(self):
        while self.Span.End != self.Len:
            self.do_key()
            self.do_value()

        if len(self.Keys) != len(self.Values):
            print("ERROR: Key value mismatch")
            return()
        
        Cnt = 0
        while Cnt != len(self.Keys):
            Key = self.Keys[Cnt].from_string(self.String)
            Value = self.Values[Cnt].from_string(self.String)
            self.KV[Key] = Value 
            Cnt += 1

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
    # initialise the class variables
    def __init__(self, Str):
        self.String = Str
        self.Len = len(Str)
        self.Span = Span(0,0)
        self.KV.clear()
        self.Values.clear()
        self.Keys.clear()

class KVSep(KVBase):
    def __init__(self,Str,KSep,VSep):
        self.String = Str
        self.Len = len(Str)
        self.KSep = KSep
        self.VSep = VSep
        self.Span = Span(0,0)
        self.KV.clear()
        self.Values.clear()
        self.Keys.clear()

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
    String = "satisfaction=good, name=Barry Robinson, employer=Northrup Grumman, asperation=principal engineer"
    P1 = KVDefault(String)
    P1.run_parser()
    P1.print()
    String = "target=Moriarty, detective=Holms, assistant=Watson"
    P1.reset(String)
    P1.run_parser()
    P1.print()

    String = "satisfaction&good# name&Barry Robinson# employer&Northrup Grumman# asperation&principal engineer"
    P2 = KVSep(String,'&','#')
    P2.run_parser()
    P2.print()

    print(P1.KV == P2.KV)

test_span() 

test_parsers()