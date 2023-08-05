# Json Comment

A wrapper to JSON parsers allowing comments and multiline strings

- - -

## Dependencies

Python 2.7, 3.3

### Optional

ujson 1.30+

- - -

## Description

JSON Comment allows to parse JSON files or strings with:

* Single and Multi line comments
* Multi line data strings

This package works with any JSON parser which supports:

* `load(fp, ...)` to parse files
* `loads(s, ...)` to parse strings

by adding a preprocessor to these calls.

- - -

### Comments

* `#` and `;` are for single line comments
* `/*` and `*/` enclose multiline comments

Inline comments are **not** supported

- - -

### Multiline strings

Any string can be multiline, even object keys.

* Multiline strings start and end with `"""`, like in python
* The preprocessor merges all lines to a single standard string
* A single trailing space is kept, if present
* New line is not kept. To hard code new lines in the string, use `\\n`

- - -

## Usage

### Install

`pip install jsoncomment`

OR

* Download source
* `python setup.py install`

### Call Example

	import json
	from jsoncomment import JsonComment

	string = "[]"
	parser = JsonComment(json)
	parsed_object = parser.loads(string)

### Examples

Added in the /examples directory

- - -

## Source

[Source](https://bitbucket.org/Dando_Real_ITA/json-comment/overview) code available with MIT license on Bitbucket.

- - -

## Contact

Dando Real ITA @ [Steam Profile](http://steamcommunity.com/id/dandorealita)
