# Pelican FrontMark

[![CI](https://github.com/noirbizarre/pelican-frontmark/actions/workflows/ci.yml/badge.svg)](https://github.com/noirbizarre/pelican-frontmark/actions/workflows/ci.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/noirbizarre/pelican-frontmark/main.svg)](https://results.pre-commit.ci/latest/github/noirbizarre/pelican-frontmark/main)
[![codecov](https://codecov.io/gh/noirbizarre/pelican-frontmark/branch/main/graph/badge.svg?token=CQBWEzzG4w)](https://codecov.io/gh/noirbizarre/pelican-frontmark)
[![License][license-badge]][license-badge-url]
[![Format][format-badge]][format-badge-url]
[![Supported versions][python-version-badge]][python-version-badge-url]

A Pelican CommonMark/Front Matter reader.

This reader marse Markdown files with YAML frontmatter headers and formatted using the CommonMark specifications.


## Requirements

Pelican FrontMark works with Pelican 4+ and Python 3.7+

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

### Syntax highlighting

By default, `FrontMark` outputs code blocks in a standard html5 way,
ie. a `pre>code` block with a language class.
This allow to use any html5 syntax highlight JavaScript lib.

You can force Pygments usage to output html4 pre rendered syntax highlight
by setting `FRONTMARK_PYGMENTS` to `True` for default parameters
or manually setting it to a dict of Pygments HtmlRenderer parameters.

```python
FRONTMARK_PYGMENTS = {
    'linenos': 'inline',
}
```

### Settings

- **`FRONTMARK_PARSE_LITERAL`**: `True` by default. Set it to `False` if you don't want multiline string literals (`|`)
  to be parsed as markdown.

- **`FRONTMARK_PYGMENTS`**: Not defined by default and output standard html5 code blocks.
  Can be set to `True` to force Pygments usage with default parameters or a `dict` of
  [Pygments parameters][pygments-options]


### Registering custom YAML types

You can register custom YAML types using the `frontmark_yaml_register` signal:

```python
from pelican.plugins.frontmark.signals import frontmark_yaml_register


def upper_constructor(loader, noder):
    return loader.construct_scalar(node).upper()


def register_upper(reader):
    return '!upper', upper_constructor


def register():
    frontmark_yaml_register.connected(register_upper):
```

## Testing

To test the plugin against all supported Python versions, run tox:

```shell
tox
```

To test only within your current Python version with pytest:

```shell
pdm sync -G:all  # Install with test dependencies
pdm test  # Launch pytest test suite
```


[license-badge]: https://img.shields.io/pypi/l/pelican-frontmark.svg
[license-badge-url]: https://pypi.python.org/pypi/pelican-frontmark
[format-badge]: https://img.shields.io/pypi/format/pelican-frontmark.svg
[format-badge-url]: https://pypi.python.org/pypi/pelican-frontmark
[python-version-badge]: https://img.shields.io/pypi/pyversions/pelican-frontmark.svg
[python-version-badge-url]: https://pypi.python.org/pypi/pelican-frontmark
[pygments-options]: http://docs.getpelican.com/en/stable/content.html#internal-pygments-options
