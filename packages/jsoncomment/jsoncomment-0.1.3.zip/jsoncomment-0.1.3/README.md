
# Json Comment

A wrapper to JSON parsers allowing comments and multi line strings

- - -

## Dependencies

Python 2.7, 3.3

### Optional

ujson 1.30+

- - -

## Description

This package allows to parse JSON files or strings with comments and multi line strings.

- - -

### Comments

* `#` and `;` are for single line comments
* `/*` and `*/` enclose multi line comments

Inline comments are **not** supported

- - -

### Multi line strings

Any string can be multi line, even object keys.

* Multi strings start and end with `"""`, like in python
* The preprocessor merges all lines to a single standard string
* No edge space or new line is kept. To hard code new lines in the string, use `\\\n`

### Notes

JSON Comment works with any JSON parser which supports "load" and "loads", by adding a preprocessor to these calls.

- - -

## Usage

### Install

pip install jsoncomment

python setup.py install

### Examples

Added in the examples directory

- - -

## Contact

Dando Real ITA @ [Steam Profile](http://steamcommunity.com/id/dandorealita)
