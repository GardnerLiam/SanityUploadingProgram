import re

remove_excess_newlines = lambda s: re.sub(r"(\n+)", r"\n", s.strip())

def is_blog(markdown):
    return_array = [False]
    if "<hr>" in markdown:
        beginning, content = markdown.split("<hr>")
        beginning = remove_excess_newlines(beginning)
        beginning = re.sub(r"(\n+)", r"\n", beginning.strip())
        if beginning[:2] == "# ":
            title, summary = beginning.split("\n")
            return_array[0] = True
            return_array += [title[2:], summary, remove_excess_newlines(content)]
    return return_array


