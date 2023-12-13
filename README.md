# Sanity Uploading Program

The sanity document uploader automatically formats markdown documents into Sanity's document JSON format, then uploads them. It is designed specifically for blog posts, but can be adapted for other pages (probably). The document uploader preserves all text stylizing, including headers (levels 2-5), bold, italics, and links. The document uploader does not work with images, as those require access to Cloudinary and the JSON looks really scary. 

## Markdown Blog Format

A blog document itself has a specific (yet simple) format to it which the program searches for and parses. The format is as follows:

```markdown
# Title

Summary goes here

<hr>

Rest of document goes here

```

`<hr>` is used specifically to split the title and summary from the rest of the blog. The title must always be a level-1 heading, appearing at the top of the document. The summary must always appear below it, and `<hr>` must appear below the summary. The whitespace between the title, summary, and `<hr>` does not affect processing.

For the rest of the document, only level-2 to level-5 headers (specified by repeating `#`) onward can be used. Italicizing and bolding is done by surrounding text with one or two asterisks:  `*italicized*`, `**bolded**`. While underscores are supported in markdown, I did not care to implement this. Links are done by specifying the link text in square brackets, and the link url in parentheses afterwards: `[link text](link url)`.  I have no clue how images will appear when uploading, but as they are not handled by the program it is not recommended to leave them in. I would imagine that they will appear as an exclamation mark, followed by a link to the image though. 

### Ignoring Formatting

If the blog format is not used, not only will I be sad, but the program *should* just consider the entire document body as content. This has not been explicitly tested, but it probably works. In this case, properties like the blog title and summary can be specified using either field borrowing, or field uploading (through JSON) discussed below. 

### Handling Sanity's Document Formatting

Sanity has many document properties which are required to be unique. Sometimes the uniqueness is only required within a given document (like with `_key` properties) and other times it is required throughout the entire database (like with `_id` and `slug`). For the `_key` property, the document automatically generates unique identifiers as necessary. When using field borrowing, the program will ensure that any keys from the borrowed fields will not be regenerated for other applications. This ensures that duplicate keys cannot arise when importing field information. 

Document ID's are generated automatically when uploading a document using Sanity's CLI. Sanity ensures that any uploaded document will have its own unique ID. The program integrates with Sanity's CLI, and as a result does not directly generate the document ID. 

There are no other safeguards in place to prevent field/property duplication. This falls on the responsibility of the user to ensure that properties such as `slug` are unique. The `_key` property and the `_id` property are taken care of. 

## CLI Arguments

There are several arguments which can be passed into the document uploader, but only one is required. They are outlined in the following table.

|Name|short option|long option|values|description|
|---|---|---|---|---|
|Input|`-i`|`--input`|Path to markdown file|Provides a path to the markdown file to be uploaded.|
|Reference ID|`-d`|`--doc-id`|ID of existing document|Allows for certain fields to be copied over from the specified document.|
|Field Borrow|`-fb`|`--field-borrow`|List of fields to be copied over|Allows for specified fields to be copied over from another document. **Requires document ID to be specified**.|
|Field Upload|`-fu`|`--field-upload`|Path to JSON file|Provides a path to a local JSON file with specified fields for the document.|
|Auto-Publish|`-P`|`--publish`|None|Automatically publishes document upon upload.|

There are two additional arguments which rework the way the program runs. These arguments are run with the program itself.

|Name|short option|long option|description|
|---|---|---|---|
|Help|`-h`|`--help`|Displays this and the above table in the command line.|
|Read Docs|`-r`|`--read-docs`|Opens the documentation in your default browser.|

All documents are uploaded as drafts. This can be disabled by specifying `-P` or `--publish`, which automatically publishes the document. 

Specifying a reference document without any fields to borrow (not using `-fb` or `--field-borrow`) will automatically borrow the following fields:

- topic tags
- craft tags
- featured posts

Specifying fields to borrow will override this list, not append to it, so using `-fb blogTitle` will only copy over the blog title and not the fields listed above. 

### List of Fields

Fields are specified by their property name in Sanity's JSON format. This means that something like "blog title" is spelt as `blogTitle`. The following is a list of all field names, all of which can be specified using the `-fb` argument. 

`blogAuthors`, `blogTitle`, `content`, `craftTags`, `featuredMediaType`, `featuredPhoto`, `featuredPosts`, `publishDate`, `slug`, `summary`, `topicTag`.

**Specifying fields whose contents come from the input document will be overwritten.**

There is an ordering to how fields are updated in the document. It is first from the document specified in the input, then the fields borrowed from the reference document, then the fields specified using a given JSON file. The intended use is that fields which use reference properties (`_ref`) can be copied over using field borrowing, and fields which are more human-legible can be specified directly using this uploading mechanic. While overlap is supported, it should be used with caution. 

### Examples

Here are some examples of uploading documents:

- `python3 sup.py -i {filehere}`: This will upload the file as a blog. The blog title, summary, and content will be extracted from the file (assuming appropriate formatting) and will be filled in appropriately. All other fields will remain empty
- `python3 sup.py -i {filehere} -d {docID}`: This will upload the file as a blog, just as above it will fill in the blog title, summary, and content. The topic tags, craft tags, and featured posts of the document whose ID was specified in `{docID}` will be copied over into the uploaded document as well.  
- `python3 sup.py -i {filehere} -d {docID} -fb topicTags featuredMediaType`: This will upload the document as a blog and copy over the topic tags and featured media type (almost always an image) from the reference document. Since `-fb` was specified with parameters, **this does not copy over the fields in the above list**.
- `python3 sup.py -i {filehere} -d {docID} -fb`: This will upload the file as a blog and does not copy over any fields. This includes the ones specified above. No additional fields from the reference document will be copied. This is equivalent to the first example.
- `python3 sup.py -i {filehere} -fb {fields here}`: **This does not work.** Fields are specified with nowhere to borrow them from. 
- `python3 sup.py -i {filehere} -P`: This will automatically publish the uploaded document. By default (without specifying `-P`), documents are uploaded as drafts. 

For using the `-fu` or `--field-upload` argument, a JSON file is required which contains the field names and values. An example of the contents of such a file follows.

```json
{
  "slug": "test-document",
  "featuredMediaType": "photo",
  "publishDate": "2023-12-13"
}
```

This file specifies the document's slug, featured media type and blog authors. In general, it is expected that this feature will be used to specify properties such as slug, publish date, featured media type, summary, blog title, or any such properties whose values are easily readable. 

Once again, any fields specified in the JSON file will override those specified in the reference. For example, if `featuredMediaType` was specified as video in the reference, but photo in the JSON file, the uploaded document will use photo for `featuredMediaType`.  The following examples show how to use the field uploading argument:

- `python3 sup.py -i {filehere} -fu {fieldfilehere}`: This uploads the document and takes the fields specified in the field file
- `python3 sup.py -i {filehere} -d {docID} -fb {fields here} -fu {fieldfilehere}`: This uploads the document, borrowing the fields from the reference document and including the fields from the field file.

