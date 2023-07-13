
# Simple python key value parser
 
# Turn a string into a dict object
class KVParser:
    # Key and Value seperators
    KSep = '='
    VSep = ','

    # Variables
    String = ''
    Key = ''
    Value = ''
    Len = 0
    Place = 0

    # The dict object we will construct
    KV = {}

    # eat up spaces and KV seperators
    def eat_up_garbage(self):
        Place = 0
        while self.String[Place] == ' ':
            Place += 1

        if Place != 0:
            self.Place += Place
            self.String = self.String[Place:self.Len]

        if(self.String):
            if self.String[0] == self.KSep or self.String[0] == self.VSep:
                self.String = self.String[1:self.Len]
                Place = 0
                while self.String[Place] == ' ':
                    Place += 1
                
                if Place != 0:
                    self.Place += Place
                    return self.String[Place:self.Len]

                return self.String
            
        return self.String

    def do_value(self):
        Word = ''
        self.String = self.eat_up_garbage()
        Place = 0
        for Chr in self.String:
            if Chr != self.VSep:
                Word += Chr
            elif Chr == self.VSep:
                self.Value = Word
                break
            elif Chr == self.KSep:
                return -1
            Place += 1

        # Catch end of string for last vale
        if (self.Place + Place) == self.Len:
            self.Value = Word
        
        # update the string and place
        self.Place += Place + 1
        self.String = self.String[Place:self.Len]
            

    def do_key(self):
        Word = ''
        self.String = self.eat_up_garbage()
        Place = 0
        for Chr in self.String:
            if Chr != self.KSep:
                Word += Chr
            elif Chr == self.KSep:
                self.Key = Word
                break
            elif Chr == self.VSep:
                return -1
            Place += 1

        self.Place += Place + 1
        self.String = self.String[Place:self.Len]    

    def run_parser(self):
        while self.String:
            self.do_key()
            self.do_value()

            self.KV[self.Key] = self.Value

    def print(self):
        print(self.KV)

class KVDefault(KVParser): 
    # initialise the class variables
    def __init__(self, Str):
        self.String = Str
        self.Len = len(Str)

class KVSep(KVParser):
    def __init__(self,Str,KSep,VSep):
        self.String = Str
        self.Len = len(Str)
        self.KSep = KSep
        self.VSep = VSep

# Create objects and parse a string
def test_parsers():
    # Test the parsers
    String = "satisfaction=good, name=Barry Robinson, employer=Northrup Grumman, asperation=principal engineer"
    P1 = KVDefault(String)
    P1.run_parser()
    P1.print()

    String = "satisfaction&good# name&Barry Robinson# employer&Northrup Grumman# asperation&principal engineer"
    P2 = KVSep(String,'&','#')
    P2.run_parser()
    P2.print()

    print(P1.KV == P2.KV)


test_parsers()