# Pelican FrontMark

[![Build Status](https://travis-ci.org/noirbizarre/pelican-frontmark.svg?branch=master)](https://travis-ci.org/noirbizarre/pelican-frontmark)
[![Coverage Status](https://coveralls.io/repos/github/noirbizarre/pelican-frontmark/badge.svg?branch=master)](https://coveralls.io/github/noirbizarre/pelican-frontmark?branch=master)
![License](https://img.shields.io/pypi/l/pelican-frontmark.svg)
![Format](https://img.shields.io/pypi/format/pelican-frontmark.svg)
![Supported versions](https://img.shields.io/pypi/pyversions/pelican-frontmark.svg)


A Pelican CommonMark/Front Matter reader.

This reader marse Markdown files with YAML frontmatter headers and formatted using the CommonMark specifications.


## Requirements

Pelican FrontMark works with Pelican 3.7+ and Python 3.3+

## Getting started

Install `pelican-frontmark` with pip:

```shell
pip install pelican-frontmark
```

And enable the plugin in you `pelicanconf.py` (or any configuration file you want to use):

```Python
PLUGINS = [
    '...',
    'frontmark',
    '...',
]
```

## Files format

Frontmark will only recognize files using `.md` extension.

Here an article example:

```markdown
---
title: My article title
date: 2017-01-04 13:10
modified: 2017-01-04 13:13
tags:
  - tag 1
  - tag 2
slug: my-article-slug
lang: en
category: A category
authors: Me
summary: Some summary
status: draft

custom:
  title: A custom metadata
  details: You can add any structured and typed YAML metadata

---

My article content

```

## Advanced configuration

### Settings

- `FRONTMARK_PARSE_LITERAL`: `True` by default. Set it to `False` if you don't want multiline string literals (`|`)
  to be parsed as markdown.

### Registering custom YAML types

You can register custom YAML types using the `frontmark_yaml_register` signal:

```python
from frontmark.signals import frontmark_yaml_register


def upper_constructor(loader, noder):
    return loader.construct_scalar(node).upper()


def register_upper(reader):
    return '!upper', upper_constructor


def register():
    frontmark_yaml_register.connected(register_upper):
```
