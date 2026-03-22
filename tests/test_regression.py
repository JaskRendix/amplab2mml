from lxml import etree

from app.builders.b2mml_builder import build_b2mml_xml
from app.pipeline import run_pipeline_from_file

NS = "http://www.wbf.org/xml/b2mml-v0400"


def _normalise(root):
    for tag in ["CreationDateTime", "PublishedDate"]:
        for el in root.findall(f".//{{{NS}}}{tag}"):
            el.text = ""
    for el in root.iter():
        if el.text:
            el.text = el.text.strip()
        if el.tail:
            el.tail = el.tail.strip()
    for comment in root.xpath("//comment()"):
        comment.getparent().remove(comment)


def _canonicalise(root):
    from io import BytesIO

    buf = BytesIO()
    root.getroottree().write_c14n(buf)
    return buf.getvalue()


def test_output_matches_xslt_ground_truth():
    model = run_pipeline_from_file("tests/data/sample_ampla.xml")
    actual = etree.fromstring(build_b2mml_xml(model).encode())
    expected = etree.parse("tests/data/sample_b2mml_expected.xml").getroot()

    _normalise(actual)
    _normalise(expected)

    assert _canonicalise(actual) == _canonicalise(expected)
