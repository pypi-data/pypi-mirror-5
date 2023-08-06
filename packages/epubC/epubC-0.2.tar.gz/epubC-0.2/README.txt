epubC - .epub file creator
==========================

Creates .epub files according to idpf standards.

- Requires lxml - checked with 2.2.6
- Works with Python 3.1.2

Installation
============

Packaged using distutils, install using

python setup.py install

Usage
=====

Example of use:
import epubC

ep = epubC.Epub("Title", "Author", "ID")

As specifed, ID should be a unique identifier such as an ISBN. Attribs are set on the object
for easy change.

Add to file:

ep.add("content.html", "application/xhtml+xml", io.StringIO(html), "Chapter 1")
ep.add("test.css", "text/css", io.StringIO(css))

- arcname will be given to the file internally, in case other files reference it.
- media_type is also added internally, here set as valid XHTML
- data is a file-like object to with data to be added
- content_title is used for constructing markers in the file

At present, epubC doesn't understand hierarchical directory structures, so arcname must be
a simple name. Otherwise, results are undefined ;) Best to format the input so it only references
other files in a 'flat' way.

media_type is required internally. Mostly contents are required to be valid XHTML if in the
main reading order.

If content_title is omitted, content is added as a resource to the file. Will not appear
in the main reading order.
	
ep.write("test.epub")

Creates the final file in name specified. No extensions are added, so specify full path.
	
ep.close()

Frees up temporary files made in the process. Call this unless you want your storage
littered with files.

Context managers are also supported, so:
with epubC.Epub("Title", "Author", "ID") as ep:
	ep.add("content.html", "application/xhtml+xml",	io.StringIO(html), "Chapter 1")
	ep.write("test.epub")

In addition to attributes specified above, additional metadata attributes are supported:

- subject, description, publisher, contributor, date, type, format, source, relation, coverage, rights

Set them on the Epub object to write as OPF metadata. Please refer to the spec for further details.
Lists will be written as multiple tags and dates converted from Python datetime.date objects.	


Known Issues/Improvements
=========================

- No way of setting depth within an epub file instead of one flat sectioning.

and probably many more!
