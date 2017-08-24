from xml.etree import ElementTree as etree  # nosec - see usage below

from django.template import Context, Template


def _gen_link(content):
    """Shorthand for passing the content into a template and rendering"""
    text = "{% load macros %}" + content
    as_str = Template(text).render(Context({}))
    # Safe because: we've constructed the XML
    as_xml = etree.fromstring("<ROOT>{}</ROOT>".format(as_str))  # nosec
    anchors = as_xml.findall('.//a')
    assert len(anchors) > 0
    return anchors[0]


def test_external_link_no_optional():
    """The classes and title fields are optional. We should generate an
    appropriate link"""
    anchor = _gen_link(
        '{% external_link url="http://example.com/path" text="Click" %}')
    assert anchor.get('target') == '_blank'
    assert anchor.get('href') == 'http://example.com/path'
    assert 'title' not in anchor.attrib
    assert 'aria-label' in anchor.attrib
    assert 'Click' in anchor.text


def test_external_link_classes_title():
    """The classes and title fields _can_ be added"""
    anchor = _gen_link(
        '{% external_link url="url" text="text" classes="some here" '
        'title="My Title" %}')
    assert anchor.get('title') == 'My Title'
    assert 'some here' in anchor.get('class')


def test_external_link_is_escaped():
    # LXML decodes the value for us, so let's look at the raw markup
    text = ('{% load macros %}'
            '{% external_link url="http://example.com/?param=1&other=value" '
            'text="value" %}')
    as_str = Template(text).render(Context({}))
    assert 'http://example.com/?param=1&amp;other=value' in as_str


def test_search_for():
    """Macro should url-encode search terms."""
    anchor = _gen_link(
        '{% search_for terms="has spaces" reg="1234" version="vvv" %}')
    assert '1234' in anchor.get('href')
    assert 'vvv' in anchor.get('href')
    assert 'has%20spaces' in anchor.get('href')
