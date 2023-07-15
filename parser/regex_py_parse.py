import re


Re = '^aws: (?P<json>{.*})'
St = 'aws: {"name":"Barry Robinson","position":"Lead cyber engineer"}'
Match = re.search(Re, St)
J = Match.group('json') 
if J is not None:
    print('aws json: ',J)
