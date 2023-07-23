# Test python code 

All this code is from a basic Python course. Some of it is me messing around with Python 3 to see what it can do. The stuff in parser is a made up project to create a parsing architecture in python capable of parsing log messages into some kind of meaningfull `json` output.

## course

Test programs and excersises relating to plurasight [Core python3: getting started](https://app.pluralsight.com/library/courses/getting-started-python-core/table-of-contents) course on [Pluralsight](https://app.pluralsight.com/library/). 
## parser

The `KV` parser in `kv_py_parse.py` is a very basic `KV` that translates a string in the form `key` = `value` to a dict object. No type conversion is done and error checking is minimal. 

The `framework` alows for rules to be created that can direct the parser via actions. The actions tell the framework weather a parsed value should be mapped as a token or reparsed by an engine to further reduce the values.

The framework can be executed by running `./framework.py <rules dir> <message>` where

    rules dir: A directory containing YAML rule files
    message: A message the the rules can decode

An example rule file is presented beow 

```yaml
- id: bf1d64ad-9694-4317-b7a6-55e9a4915437
  name: test rule
  patterns: 
    - id: f28a4fcc-32dd-4c4b-afd6-4aca3e4f5537
      name: aws json
      type: regex 
      partition: root
      pattern: '^aws: (?P<json>{.*})'
      triggers:
        - name: json
          format: regex
          partition: aws regex
    - id: eb4963b9-3fa5-4338-8a40-01a35fecc782
      name: aws regex
      type: regex
      partition: aws regex
      pattern: '^{"name":"(?P<name>[\w ]+)","satisfaction":"(?P<satisfaction>[\w ]+)"}'
      map:
        name: name
        satisfaction: value
```

With this rule the string `'aws: {"name":"Barry Robinson","value":"high"}'` is first matched by trhe pattern `f28a4fcc-32dd-4c4b-afd6-4aca3e4f5537` whose trigger is setup to forward the text extracted by the `json` capture group to to a `regex` partition called `aws regex`. 

Pattern `eb4963b9-3fa5-4338-8a40-01a35fecc782` recives the text and parses `name` and `value`, which, due to the `map` statement is maped to the tokens `name` and `value`

If no rules with patterns for the message exists, an empty map is returned. 

If a rule (or set of rules and patterns) exists that can parse the message, a map of `{'token name':'token value'}` is returned for the tokanized message. 

The above rule, for the message `'aws: {"name":"Barry Robinson","satisfaction":"high"}'` yields the output `{"rule": "bf1d64ad-9694-4317-b7a6-55e9a4915437", "pattern": ["f28a4fcc-32dd-4c4b-afd6-4aca3e4f5537", "eb4963b9-3fa5-4338-8a40-01a35fecc782"], "tokens": {"name": "Barry Robinson", "value": "high"}}`

With `jq formating` the command `./framework.py resources/framework_two/ 'aws: {"name":"Barry Robinson","satisfaction":"high"}' | jq` will format to

```json
{
  "rule": "bf1d64ad-9694-4317-b7a6-55e9a4915437",
  "pattern": [
    "f28a4fcc-32dd-4c4b-afd6-4aca3e4f5537",
    "eb4963b9-3fa5-4338-8a40-01a35fecc782"
  ],
  "tokens": {
    "name": "Barry Robinson",
    "value": "high"
  }
}
```

For more details about the parser please checkout the [parser design document](parser/docs/design.md).

## Note 

1. Currently only supports `regex` parsing engine
2. Design for `kv` and `json` engines needs to assess uniqueness of `match` criteria on the pattern

### Todo 

1. Finish the `KV` Parser class 
2. Finish the `JSON` Parser class
3. Finish mapping for `jq path` spacified patterns for `KV` and `JSON`  

## Old 

Old python `first attempts` kept to show progress. Other progress can be gleaned by going through the git history.