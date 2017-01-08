import os

from pelican import readers, Pelican
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import SafeDatetime

from frontmark.reader import FrontmarkReader
from frontmark.signals import frontmark_yaml_register


TEST_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(TEST_DIR, 'data')


def get_settings(**kwargs):
    settings = DEFAULT_CONFIG.copy()
    for key, value in kwargs.items():
        settings[key] = value
    return settings


def _path(*args):
    return os.path.join(DATA_PATH, *args)


def read_content_metadata(path, **kwargs):
    r = FrontmarkReader(settings=get_settings(**kwargs))
    return r.read(_path(path))


def read_file(path, **kwargs):
    r = readers.Readers(settings=get_settings(**kwargs))
    return r.read_file(base_path=DATA_PATH, path=path)


def assert_dict_contains(tested, expected):
    assert set(expected).issubset(set(tested)), 'Some keys are missing'
    for key, value in expected.items():
        assert tested[key] == value
    # assert all(item in superset.items() for item in subset.items())


def test_read_markdown_and_metadata():
    page = read_file('page.md')
    assert page
    assert page.title == 'Some page'
    assert page.content == '<p>This is a simple markdown file</p>'


def test_typed_metadata():
    content, metadata = read_content_metadata('metadata.md')
    expected = {
        'title': 'Metadata',
        'list': ['a', 'b', 'c'],
        'date': SafeDatetime(2017, 1, 6, 22, 24),
        'int': 42,
        'bool': False,
        'summary': '<p>a summary</p>',
    }
    assert_dict_contains(metadata, expected)


def test_markdown_only():
    content, metadata = read_content_metadata('markdown-only.md')
    assert metadata == {}
    assert content == '<p>Only markdown</p>'


def test_metadata_only():
    content, metadata = read_content_metadata('meta-only.md')
    assert metadata == {'title': 'Meta only'}
    assert content == ''


def test_multiline_rendering():
    _, metadata = read_content_metadata('multiline.md')
    assert_dict_contains(metadata, {
        'rendered': '<p>This should be rendered</p>',
        'notrendered': 'This shouldn\'t be rendered\n',
        'markdown': '<p>This should be rendered</p>',
    })


def test_multiline_rendering_disabled():
    _, metadata = read_content_metadata('multiline.md', FRONTMARK_PARSE_LITERAL=False)
    assert_dict_contains(metadata, {
        'rendered': 'This should be rendered\n',
        'notrendered': 'This shouldn\'t be rendered\n',
        'markdown': '<p>This should be rendered</p>',
    })


def test_hr():
    content, _ = read_content_metadata('hr.md')
    assert '<hr/>' in content.replace(' ', '')


def test_markdown_only_with_hr_start():
    content, metadata = read_content_metadata('hr-start.md')
    assert metadata == {}
    assert content.replace(' ', '') == '<hr/>\n<p>Starts</p>'


def register_custom_type(reader):
    return '!custom', lambda l, n: l.construct_scalar(n).upper()


def test_custom_types():
    with frontmark_yaml_register.connected_to(register_custom_type):
        _, metadata = read_content_metadata('types.md')
    assert metadata['custom'] == 'TEST'


def test_wrong_custom_type_warn_only():
    with frontmark_yaml_register.connected_to(lambda r: 'missing arg'):
        read_content_metadata('page.md')


def test_pelican_registeration():
    settings = get_settings(PLUGINS=['frontmark'])
    p = Pelican(settings)
