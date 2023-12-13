import re
import json
import uuid
import time
import hashlib

def generate_hex_identifier(exclusion_list):
    """
    Uses current time to generate unique hex identifier for _key property
    
    Args:
    exclusion_list (list): A list of predefined _key values to ignore.
                           Used to ensure unique _key across documents

    Returns:
    str: A 13 character unique hexadecimal identifier. 
    """
    unique_string = str(time.time()) + str(uuid.uuid4())
    hash_object = hashlib.sha256(unique_string.encode())

    # Return the required number of characters
    curhex = hash_object.hexdigest()[:13]
    while curhex in exclusion_list:
        unique_string = str(time.time()) + str(uuid.uuid4())
        hash_object = hashlib.sha256(unique_string.encode())
        curhex = hash_object.hexdigest()[:13]
    return curhex

def generate_child(exclusion_list):
    """
    Creates child object template
    
    Args:
    exlcusion_list (list): Used to fill _key property.
    
    Returns:
    dict: Child object template.
    """
    return {
        "_key": generate_hex_identifier(exclusion_list),
        "_type": "span",
        "marks": []
    }
    
def extract_links(text):
    """
    Extracts linked and non-linked parts of the text.
    
    Args:
    text (str): The input text with potential markdown links.

    Returns:
    list: A list of tuples with the text and its associated link or 0.
    """
    
    # Pattern to find markdown links
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    # List to store results
    result = []
    
    # Last index processed
    last_idx = 0

    # Find all matches
    for match in re.finditer(pattern, text):
        # Text before the link
        before_link = text[last_idx:match.start()]
        if before_link:
            result.append((before_link, 0))

        # Link text and URL
        link_text = match.group(1)
        link_url = match.group(2)
        result.append((link_text, link_url))

        # Update last index
        last_idx = match.end()

    # Add remaining text after the last link
    if last_idx < len(text):
        result.append((text[last_idx:], 0))

    return result


def parse_markdown(text):
    """
    Creates list of line formatting with specific tags for formats.
    
    Args:
    text (str): Particular line in the document.

    Returns:
    list: A list of tuples containing substrings.
    The tuples contain, in order:
        - The particular substring
        - The link url if applicable
        - 0 if there is no formatting
        - 1 if italicized formatting
        - 2 if bold formatting
    Multiple of these formatting identifiers can be present in one tuple.
    """
    # Regex pattern to split the text into formatted and non-formatted parts
    pattern = r'(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*)'
    parts = re.split(pattern, text)
    formlist = []

    for part in parts:
        if not part:
            continue

        if part.startswith('***'):
            stripped_text = part.strip('*')
            formlist.append((stripped_text, 1, 2))
        elif part.startswith('**'):
            stripped_text = part.strip('*')
            formlist.append((stripped_text, 2))
        elif part.startswith('*'):
            stripped_text = part.strip('*')
            formlist.append((stripped_text, 1))
        else:
            formlist.append((part, 0))
    
    results = []
    for i in formlist:
        regexp = re.compile(r"\[(.*?)\]\((.*?)\)")
        if regexp.search(i[0]):
            for j in extract_links(i[0]):
                j = list(j)
                if j[1] == 0 and i[1] != 0:
                    j = [j[0]] + i[1:]
                    j = tuple(j)
                elif j[1] == 0 and i[1] == 0:
                    j = tuple(j)
                else:
                    j += i[1:]
                    j = tuple(j)
                results.append(j)
        else:
            results.append(i)

    return results

def markdown_to_json(markdown_text, exclusion_list):
    """
    Converts markdown document into Sanity content object in JSON form.
    
    Args:
    markdown_text (str): The markdown document in string format
    exclusion_list (list): List of _key values to be excluded in generation.


    Returns:
    JSON output for Sanity document content. 
    """

    # Split the markdown text into lines
    lines = markdown_text.strip().split('\n')

    # Function to determine the style of text
    def determine_style(text):
        """
        Determines if a specific line is a header or not.
        
        Args:
        text (str): The particular line in the document.
        
        Returns:
        Either header style identifier or 'normal' indicating no header.
        """
        if text.startswith('#'):
            return 'h' + str(len(re.match(r'\#+', text).group(0)))
        else:
            return 'normal'

    # Function to parse text and marks
    def parse_text_and_marks(text):
        """
        Produces line children objects and inline link identifiers
        
        Args:
        text (str): The particular line in the document

        Returns:
        children (list): List of child objects per line adhering to Sanity's content formatting.
        link_dict (dict): Dictionary connecting _key identifiers to URLs.
        """
        children = []
        link_dict = {}

        parsed = parse_markdown(text)
        for i in parsed:
            child = generate_child(exclusion_list)
            child['text'] = i[0]
            if isinstance(i[1], str):
                hex_link = generate_hex_identifier(exclusion_list)
                link_dict[hex_link] = i[1]
                child['marks'].append(hex_link)
            if 1 in i:
                child['marks'].append("em")
            if 2 in i:
                child['marks'].append("strong")
            children.append(child)
        
        return children, link_dict

    # Parse the markdown line by line
    json_output = []
    for i, line in enumerate(lines, start=1):
        line_data = {"_key": generate_hex_identifier(exclusion_list), "_type": "richText", "children": []}

        # Check for bullet lists
        if line.strip().startswith('- '):
            line_data["level"] = line.count('    ') + 1
            line_data["listItem"] = "bullet"
            text = line.strip()[2:]  # Remove '- ' from the beginning
        else:
            text = line.strip()

        # Determine the style of the line
        style = determine_style(text)
        text = re.sub(r'^#+ ', '', text)  # Remove the '#' symbols from headers

        # Parse the text and marks
        children, link_dict = parse_text_and_marks(text)
        line_data["children"] = children
        line_data['style'] = style
        line_data['markDefs'] = []
        if len(link_dict) > 0:
            for key, val in link_dict.items():
                line_data['markDefs'].append({"_key": key, "_type": "inlineLink", "href": val})

        # Skip empty lines
        if not line_data["children"]:
            continue

        json_output.append(line_data)

    return json_output


remove_excess_newlines = lambda s: re.sub(r"(\n+)", r"\n", s.strip())

def blog_parser(markdown):
    """
    Examines a markdown document for the presence of <hr> separating
    a ittle (level-1 header) and summary from the content of the document

    If present, will return the document broken down into title, summary, content.    
    
    Args:
    markdown (str): A markdown document 

    Returns:
    list: A list of at most two elements
          The first element is a boolean representing if the document is a blog.
          If the first element is true, the second element is an array of the blog.
          The array is broken down as
            - Title
            - Summary
            - Content
    """

    return_array = [False, []]
    if "<hr>" in markdown:
        beginning, content = markdown.split("<hr>")
        beginning = remove_excess_newlines(beginning)
        beginning = re.sub(r"(\n+)", r"\n", beginning.strip())
        if beginning[:2] == "# ":
            title, summary = beginning.split("\n")
            return_array[0] = True
            return_array[1] += [title[2:], summary, remove_excess_newlines(content)]
    return return_array



'''
# Example markdown text
with open("markdown_test.md", 'r') as f:
    markdown_text = f.read()

# Convert to JSON
with open('test_out.json', 'w') as f:
    f.write(json.dumps(markdown_to_json(markdown_text, []), indent=2))
'''
