
# import and use the KV parser
import kv_py_parse

String = 'name = Barry Robinson, occupation = lead cyber engineer, security clearance = awaiting clearance'
P = kv_py_parse.KVSep(String)

P.run_parser()
P.print()