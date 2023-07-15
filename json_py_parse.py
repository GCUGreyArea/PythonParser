import json

person = '{"name": "Barrt", "languages": ["English", "French"], "age":58}'
person_dict = json.loads(person)

# Output: {'name': 'Bob', 'languages': ['English', 'French']}
print( person_dict )

# Output: ['English', 'French']
print(person_dict['languages'])