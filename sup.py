from markdown_converter.markdown_formatter import markdown_to_json, blog_parser

import argparse

import webbrowser
import subprocess
import shutil
import json
import os

class ReadDocsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        doc_path = "markdown_converter/docs.html"
        webbrowser.open(f"file://{os.path.abspath(doc_path)}")
        parser.exit()


def create_parser():
    # Create the parser
    parser = argparse.ArgumentParser(description="CLI Arguments")

    # Add mandatory input file option
    parser.add_argument('-i', '--input', required=True, type=str, help="Filepath for input file")

    # Add optional template document id option
    parser.add_argument('-d', '--doc-id', required=False, type=str, help="Document ID to borrow fields from")

    # Add optional field copy option
    # Note: This is dependent on -d/--doc-id, so we will need to validate this dependency later
    parser.add_argument('-fb', '--field-borrow', required=False, nargs='*', default=None, type=str,
                        help="List fields to copy over from specified document (requires -d/--doc-id)")

    # Add optional direct publish flag
    # This flag does not take any inputs, it's a boolean flag
    parser.add_argument('-P', '--publish', action='store_true', help="Publish upon upload")

    # Add optional local field copy option
    parser.add_argument('-fu', '--field-upload', required=False, type=str, help="Filepath for fields file") 

    # Add read docs option
    parser.add_argument('-r', '--read-docs', nargs=0, action=ReadDocsAction, help="Opens documentation in default browser")

    return parser

# Function to parse and validate arguments
def parse_args():
    parser = create_parser()
    parsed_args = parser.parse_args()

    # Validate input file is actual file
    if not os.path.isfile(parsed_args.input):
        parser.error(f"The file {parsed_args.input} does not exist")

    # Validate fields file is actual file
    if parsed_args.field_upload and not os.path.isfile(parsed_args.field_upload):
        parser.error(f"The file {parsed_args.field_upload} does not exist")

    # Validate the dependency between --property-borrow and --doc-id
    if parsed_args.field_borrow and not parsed_args.doc_id:
        parser.error("--field-borrow requires --doc-id")

    return parsed_args

cache = {}

def create_cache():
    if not os.path.exists("cache"):
        os.makedirs("cache")

def delete_cache():
    shutil.rmtree("cache")

def download_document_from_id(name, doc_id):
    process = f'sanity documents get {doc_id}'.split()
    result = subprocess.run(process, capture_output=True, text=True)
    json_data = json.loads(result.stdout)
    with open(name, 'w') as f:
        f.write(json.dumps(json_data, separators=(',', ':')))
    return json_data

def upload_document(name):
    process = f'sanity documents create cache/{name}'.split()
    result = subprocess.run(process, capture_output=True, text=True)
    return result.stdout

def grab_property_from_document(doc_property, doc_id):
    global cache
    if len(cache) == 0:
        create_cache()
    doc = {}
    if doc_id in cache:
        with open(cache[doc_id], 'r') as f:
            doc = json.loads(f.read())
    else:
        doc = download_document_from_id(f'cache/tmp_doc{len(cache)}.json', doc_id)
        cache[doc_id] = f"cache/tmp_doc{len(cache)}.json"
    return doc[doc_property]

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


def create_blog_from_document(filepath, template_id=None, template_properties=[]):
    with open(filepath, 'r') as f:
        markdown_text = f.read()
    is_blog, blog_data = blog_parser(markdown_text)
    json_data = {"_id": "drafts.", "_type": "blogPost"}
    if is_blog:
        json_data["blogTitle"] = blog_data[0]
        json_data["summary"] = blog_data[1]
    if template_id is not None and len(template_properties) > 0:
        for doc_property in template_properties:
            json_data[doc_property] = grab_property_from_document(doc_property, template_id)
    keys = list(find_keys_with_name(json_data, "_key"))
    if is_blog:
        content = markdown_to_json(blog_data[2], keys)
        json_data['content'] = content
    else:
        content = markdown_to_json(markdown_text)    
        json_data['content'] = content
    return json_data

def upload_json(json_data):
    create_cache() 
    with open('cache/output.json', 'w') as f:
        f.write(json.dumps(json_data, separators=(',', ':')))
    return upload_document("output.json")
    
if __name__ == "__main__":
    args = parse_args()

    markdown_filepath = args.input
    doc_id = None
    properties = ["topicTags", "craftTags", "featuredPosts"]
    if args.doc_id:
        doc_id = args.doc_id
        if args.field_borrow is not None:
            properties = args.field_borrow

    '''
    markdown_filepath = "/Users/liamgardner/Desktop/Blog notes/Notes/Blogs/Dynamic Pricing and Inventory blog.md"
    doc_id = "f51e2190-f691-4d95-95b5-8c33683675d9"
    properties = ["blogAuthors", "topicTags", "craftTags", "featuredPosts"]
    '''

    json_data = create_blog_from_document(markdown_filepath, doc_id, properties)

    if args.field_upload:
        with open(args.field_upload, 'r') as f:
            ext = json.loads(f.read())
        for key, val in ext.items():
            json_data[key] = val

    if args.publish:
        del json_data['_id']

    print(upload_json(json_data))
    delete_cache()
