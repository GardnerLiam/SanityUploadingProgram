import re

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


# Example usage
sample_text = "This text is *italicized*, this text is **bolded**, and this text is [linked](url). Combined: ***bold and italics***, **[bold link](url)**, and *[italic link](url)*."
extract = parse_markdown(sample_text)
for i in extract:
    print(i)    

## Test the function
#test_str = "This is a *simple* test with **multiple** styles and ***combinations***, including [*links*](http://example.com)."
#print(parse_markdown(test_str))
