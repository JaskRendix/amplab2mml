from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml
from app.transformers.normalize import normalize_to_xslt_semantics


class InvalidXML(Exception):
    """Raised when XML parsing fails."""


def load_xml_from_bytes(xml_bytes: bytes):
    try:
        return etree.fromstring(xml_bytes)
    except Exception as exc:
        raise InvalidXML("Invalid XML content") from exc


def load_xml_from_file(path: str):
    try:
        with open(path, "rb") as f:
            return etree.parse(f).getroot()
    except Exception as exc:
        raise InvalidXML(f"Invalid XML file: {path}") from exc


def run_pipeline_from_root(root):
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)
    return model


def run_pipeline_from_file(path: str):
    root = load_xml_from_file(path)
    return run_pipeline_from_root(root)


def run_pipeline_from_bytes(xml_bytes: bytes):
    root = load_xml_from_bytes(xml_bytes)
    return run_pipeline_from_root(root)
