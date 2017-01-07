import collections
import logging
import re

try:
    from CommonMark import commonmark
except ImportError:  # pragma: no cover
    commonmark = False

try:
    import yaml
except ImportError as e:  # pragma: no cover
    yaml = False

from pelican.readers import BaseReader
from pelican.utils import pelican_open

from .signals import frontmark_yaml_register

log = logging.getLogger(__name__)


DELIMITER = '---'
BOUNDARY = re.compile(r'^{0}$'.format(DELIMITER), re.MULTILINE)
STR_TAG = 'tag:yaml.org,2002:str'


def markdown_constructor(loader, node):
    '''Allows to optionnaly parse Markdown in multiline literals'''
    value = loader.construct_scalar(node)
    return commonmark(value).strip()


def multiline_as_markdown_constructor(loader, node):
    '''Allows to optionnaly parse Markdown in multiline literals'''
    value = loader.construct_scalar(node)
    return commonmark(value).strip() if node.style == '|' else value


def loader_factory(reader):
    class FrontmarkLoader(yaml.Loader):
        '''
        Custom YAML Loader for frontmark

        - Mapping order is respected (wiht OrderedDict)
        '''
        def construct_mapping(self, node, deep=False):
            '''User OrderedDict as default for mappings'''
            return collections.OrderedDict(self.construct_pairs(node))

    FrontmarkLoader.add_constructor('!md', markdown_constructor)
    if reader.settings.get('FRONTMARK_PARSE_LITERAL', True):
        FrontmarkLoader.add_constructor(STR_TAG, multiline_as_markdown_constructor)
    for _, pair in frontmark_yaml_register.send(reader):
        if not len(pair) == 2:
            log.warning('Ignoring YAML type (%s), expected a (tag, handler) tuple', pair)
            continue
        tag, constructor = pair
        FrontmarkLoader.add_constructor(tag, constructor)

    return FrontmarkLoader


class FrontmarkReader(BaseReader):
    '''
    Reader for CommonMark Markdown files with YAML metadata
    '''

    enabled = bool(commonmark) and bool(yaml)
    file_extensions = ['md']

    def read(self, source_path):
        self._source_path = source_path

        with pelican_open(source_path) as text:
            metadata, content = self._parse(text)
            # metadata.setdefault('title', '-')

        return commonmark(content).strip(), self._parse_metadata(metadata)

    def _parse(self, text):
        '''
        Parse text with frontmatter, return metadata and content.
        If frontmatter is not found, returns an empty metadata dictionary and original text content.
        '''
        # ensure unicode first
        text = str(text).strip()

        if not text.startswith(DELIMITER):
            return {}, text

        try:
            _, fm, content = BOUNDARY.split(text, 2)
        except ValueError:
            # if we can't split, bail
            return {}, text
        loader_class = loader_factory(self)
        metadata = yaml.load(fm, Loader=loader_class)
        metadata = metadata if (isinstance(metadata, dict)) else {}
        return metadata, content.strip()

    def _parse_metadata(self, meta):
        """Return the dict containing document metadata"""
        formatted_fields = self.settings['FORMATTED_FIELDS']

        output = collections.OrderedDict()
        for name, value in meta.items():
            name = name.lower()
            if name in formatted_fields:
                rendered = commonmark(value).strip()
                output[name] = self.process_metadata(name, rendered)
            else:
                output[name] = self.process_metadata(name, value)
        return output


def add_reader(readers):  # pragma: no cover
    for k in FrontmarkReader.file_extensions:
        readers.reader_classes[k] = FrontmarkReader
