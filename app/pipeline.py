import logging

from lxml import etree

from app.transformers.ampla_to_b2mml import AmplaTransformer
from app.validators import validate_model

logger = logging.getLogger(__name__)


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
    transformer = AmplaTransformer(config_path="config/mapping.toml")
    model = transformer.transform(root)
    warnings = validate_model(model)
    for w in warnings:
        logger.warning(w)
    model["warnings"] = warnings
    return model


def run_pipeline_from_file(path: str):
    return run_pipeline_from_root(load_xml_from_file(path))


def run_pipeline_from_bytes(xml_bytes: bytes):
    return run_pipeline_from_root(load_xml_from_bytes(xml_bytes))
