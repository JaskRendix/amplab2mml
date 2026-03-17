from lxml import etree

from app.builders.b2mml_builder import build_b2mml_xml
from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml

NS = {"b2mml": "http://www.wbf.org/xml/b2mml-v0400"}


def test_b2mml_xml_structure(minimal_ampla_xml):
    root = etree.fromstring(minimal_ampla_xml)
    model = transform_ampla_to_b2mml(root)
    xml = build_b2mml_xml(model)

    doc = etree.fromstring(xml.encode())

    assert doc.tag.endswith("ShowEquipmentInformation")

    app_area = doc.find(".//b2mml:ApplicationArea", namespaces=NS)
    assert app_area is not None

    data_area = doc.find(".//b2mml:DataArea", namespaces=NS)
    assert data_area is not None
    assert data_area.find("b2mml:Show", namespaces=NS) is not None

    eq_info = data_area.find("b2mml:EquipmentInformation", namespaces=NS)
    assert eq_info is not None
    assert eq_info.find("b2mml:PublishedDate", namespaces=NS) is not None

    eq = eq_info.find("b2mml:Equipment", namespaces=NS)
    assert eq is not None
    assert eq.find("b2mml:ID", namespaces=NS).text == "Mine"

    cls = eq_info.find("b2mml:EquipmentClass", namespaces=NS)
    assert cls is not None
    assert cls.find("b2mml:ID", namespaces=NS).text == "Base"
