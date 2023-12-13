from markdown_formatter import markdown_to_json
import json

template = {"_type": "blogPost"}

with open("markdown_test.md", 'r') as f:
    text = f.read()

beginning, content = text.split("<hr>")

title = beginning.split("\n")[0].replace("# ", "")
summary = [i for i in beginning.split("\n")[1:] if i != ''][0]

template['blogTitle'] = title
template['summary'] = summary

template['content'] = markdown_to_json(content.strip(), [])

with open("output.json", 'w') as f:
    f.write(json.dumps(template, separators=(',', ':')))
    #f.write(json.dumps(template, indent=2))
