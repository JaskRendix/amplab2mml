from lxml import etree

from app.builders.b2mml_builder import build_b2mml_xml
from app.pipeline import run_pipeline_from_file

NS = {"b": "http://www.wbf.org/xml/b2mml-v0400"}


def roundtrip(make_model, xml: str):
    """Runs Ampla → Model → B2MML → XML roundtrip."""
    model = make_model(xml)
    b2mml_xml = build_b2mml_xml(model)
    return etree.fromstring(b2mml_xml.encode()), model


XML = """
<Ampla>
  <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
    <Item id="2" name="Plant" type="Citect.Ampla.Isa95.SiteFolder">
      <ItemClassAssociation classDefinitionId="20"/>
      <Property name="Class.DriveType">Electric</Property>
    </Item>
  </Item>
  <ClassDefinitions>
    <ClassDefinition id="10" name="Base">
      <ClassDefinition id="20" name="Crusher">
        <PropertyDefinition name="DriveType" type="System.String">Unknown</PropertyDefinition>
        <PropertyDefinition name="Manufacturer" type="System.String">ACME</PropertyDefinition>
      </ClassDefinition>
    </ClassDefinition>
  </ClassDefinitions>
</Ampla>
"""


def test_roundtrip_equipment_ids(make_model):
    doc, model = roundtrip(make_model, XML)
    ids = [el.text for el in doc.findall(".//b:Equipment/b:ID", NS)]

    model_names = []
    stack = list(model["equipment"])
    while stack:
        eq = stack.pop(0)
        model_names.append(eq.full_name)
        stack = list(eq.children) + stack

    for name in model_names:
        assert name in ids


def test_roundtrip_equipment_levels(make_model):
    doc, _ = roundtrip(make_model, XML)
    levels = [el.text for el in doc.findall(".//b:EquipmentElementLevel", NS)]
    assert "Enterprise" in levels
    assert "Site" in levels


def test_roundtrip_class_ids(make_model):
    doc, model = roundtrip(make_model, XML)
    class_ids = [el.text for el in doc.findall(".//b:EquipmentClass/b:ID", NS)]
    model_class_names = [cls.name for cls in model["classes"]]
    for name in model_class_names:
        assert name in class_ids


def test_roundtrip_property_values(make_model):
    doc, _ = roundtrip(make_model, XML)

    equipment = doc.findall(".//b:Equipment", NS)
    plant = next(
        e for e in equipment if e.findtext("b:ID", namespaces=NS) == "Mine.Plant"
    )

    props = {
        e.findtext("b:ID", namespaces=NS): e.findtext(".//b:ValueString", namespaces=NS)
        for e in plant.findall("b:EquipmentProperty", NS)
    }

    assert props["DriveType"] == "Electric"
    assert props["Manufacturer"] == "ACME"


def test_roundtrip_class_parent(make_model):
    doc, _ = roundtrip(make_model, XML)

    crusher_class = next(
        (
            e
            for e in doc.findall(".//b:EquipmentClass", NS)
            if e.findtext("b:ID", namespaces=NS) == "Crusher"
        ),
        None,
    )
    assert crusher_class is not None

    parent_prop = next(
        (
            e
            for e in crusher_class.findall("b:EquipmentClassProperty", NS)
            if e.findtext("b:ID", namespaces=NS) == "Ampla.Parent"
        ),
        None,
    )
    assert parent_prop is None


def test_roundtrip_sample_file():
    """Full round-trip on the regression fixture."""
    model = run_pipeline_from_file("tests/data/sample_ampla.xml")
    xml_out = build_b2mml_xml(model)
    doc = etree.fromstring(xml_out.encode())

    assert doc.tag.endswith("ShowEquipmentInformation")

    equipment = doc.findall(".//b:Equipment", NS)
    assert len(equipment) > 0

    classes = doc.findall(".//b:EquipmentClass", NS)
    assert len(classes) > 0
