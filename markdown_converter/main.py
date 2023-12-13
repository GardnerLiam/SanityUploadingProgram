from markdown_formatter import markdown_to_json
import json

# Assuming json_data is your JSON object
def find_keys_with_name(data, key_name):
    """
    Recursive function to find all occurrences of a given key in a nested dictionary.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_name:
                yield value
            if isinstance(value, (dict, list)):
                yield from find_keys_with_name(value, key_name)
    elif isinstance(data, list):
        for item in data:
            yield from find_keys_with_name(item, key_name)


with open("liam-test.json", 'r') as f:
    json_data = json.loads(f.read())

'''
keys = []
for i in json_data:
    for j in i.keys():
        keys.append(j)
for j in list(set(keys)):
    print(j)
'''

# Finding all "_key" properties and their values in the json_data
keys = list(find_keys_with_name(json_data, "_key"))

with open("markdown_test.md", 'r') as f:
    markdown_text = f.read()

json_data['content'] = markdown_to_json(markdown_text, keys)
json_data['_id'] = 'drafts.'
with open('output.json',  'w') as f:
    #f.write(json.dumps(json_data, indent=2))
    f.write(json.dumps(json_data, separators=(',', ':')))
