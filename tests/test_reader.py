import os

from pelican import Pelican, readers
from pelican.plugins.frontmark.reader import FrontmarkReader
from pelican.plugins.frontmark.signals import frontmark_yaml_register
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import SafeDatetime
from pyquery import PyQuery as pq

TEST_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(TEST_DIR, "data")


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
    assert set(expected).issubset(set(tested)), "Some keys are missing"
    for key, value in expected.items():
        assert tested[key] == value
    # assert all(item in superset.items() for item in subset.items())


def test_read_markdown_and_metadata():
    page = read_file("page.md")
    assert page
    assert page.title == "Some page"
    assert page.content == "<p>This is a simple markdown file</p>"


def test_typed_metadata():
    content, metadata = read_content_metadata("metadata.md")
    expected = {
        "title": "Metadata",
        "list": ["a", "b", "c"],
        "date": SafeDatetime(2017, 1, 6, 22, 24),
        "int": 42,
        "bool": False,
        "summary": "<p>a summary</p>",
    }
    assert_dict_contains(metadata, expected)


def test_markdown_only():
    content, metadata = read_content_metadata("markdown-only.md")
    assert metadata == {}
    assert content == "<p>Only markdown</p>"


def test_metadata_only():
    content, metadata = read_content_metadata("meta-only.md")
    assert metadata == {"title": "Meta only"}
    assert content == ""


def test_multiline_rendering():
    _, metadata = read_content_metadata("multiline.md")
    assert_dict_contains(
        metadata,
        {
            "rendered": "<p>This should be rendered</p>",
            "notrendered": "This shouldn't be rendered\n",
            "markdown": "<p>This should be rendered</p>",
        },
    )


def test_multiline_rendering_disabled():
    _, metadata = read_content_metadata("multiline.md", FRONTMARK_PARSE_LITERAL=False)
    assert_dict_contains(
        metadata,
        {
            "rendered": "This should be rendered\n",
            "notrendered": "This shouldn't be rendered\n",
            "markdown": "<p>This should be rendered</p>",
        },
    )


def test_default_syntax_highlighting_html5():
    """Output standard pre>code block with language class by default"""
    content, _ = read_content_metadata("highlight.md")
    pre = pq(content)
    assert pre.length == 1
    assert pre.is_("pre")
    code = pre.children()
    assert code.length == 1
    assert code.is_("code")
    assert code.has_class("language-python")
    assert code.text() == "print('Hello Frontmark')"


def test_syntax_highlighting_pygments():
    """Output Pygments rendered div.highlight>code block"""
    content, _ = read_content_metadata("highlight.md", FRONTMARK_PYGMENTS=True)
    div = pq(content)
    assert div.length == 1
    assert div.is_("div")
    assert div.has_class("highlight")
    pre = div.children()
    assert pre.length == 1
    assert pre.is_("pre")


def test_syntax_highlighting_pygments_options():
    """Pass FRONTMARK_PYGMENTS options to Pygments"""
    content, _ = read_content_metadata(
        "highlight.md",
        FRONTMARK_PYGMENTS={
            "linenos": "inline",
        },
    )
    assert pq(content).find(".linenos").length > 0


def test_syntax_highlighting_pygments_unknown_language():
    """Pygments should not fail on unkown language"""
    content, _ = read_content_metadata("highlight-unknown.md", FRONTMARK_PYGMENTS=True)
    div = pq(content)
    assert div.length == 1
    assert div.is_("div")
    assert div.has_class("highlight")
    pre = div.children()
    assert pre.length == 1
    assert pre.is_("pre")


def test_hr():
    content, _ = read_content_metadata("hr.md")
    assert "<hr/>" in content.replace(" ", "")


def test_links_in_anchors():
    content, _ = read_content_metadata("links.md")
    anchors = pq(content).find("a")
    expected = (
        "{filename}/article.md",
        "{attach}/file.pdf",
        "{index}",
        "{author}/author",
        "{category}/category",
        "{tag}/tag",
    )
    for a, expected in zip(anchors.items(), expected):
        assert a.attr.href == expected


def test_filename_in_images():
    content, _ = read_content_metadata("links.md")
    imgs = pq(content).find("img")
    expected = (
        "{filename}/image.png",
        "{attach}/image.png",
    )
    for img, expected in zip(imgs.items(), expected):
        assert img.attr.src == expected


def test_markdown_only_with_hr_start():
    content, metadata = read_content_metadata("hr-start.md")
    assert metadata == {}
    assert content.replace(" ", "") == "<hr/>\n<p>Starts</p>"


def register_custom_type(reader):
    return "!custom", lambda l, n: l.construct_scalar(n).upper()  # noqa: E741


def test_custom_types():
    with frontmark_yaml_register.connected_to(register_custom_type):
        _, metadata = read_content_metadata("types.md")
    assert metadata["custom"] == "TEST"


def test_wrong_custom_type_warn_only():
    with frontmark_yaml_register.connected_to(lambda r: "missing arg"):
        read_content_metadata("page.md")


def test_pelican_registeration():
    settings = get_settings(PLUGINS=["frontmark"])
    Pelican(settings)
