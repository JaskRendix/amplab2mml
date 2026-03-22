import csv
from io import StringIO

from lxml import etree

from app.csv_export import export_classes_csv, export_equipment_csv
from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


def make_model(xml: str) -> dict:
    return transform_ampla_to_b2mml(etree.fromstring(xml.encode()))


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


def parse_csv(text: str) -> list[dict]:
    return list(csv.DictReader(StringIO(text)))


def test_equipment_csv_headers():
    rows = parse_csv(export_equipment_csv(make_model(XML)))
    assert "full_name" in rows[0]
    assert "level" in rows[0]
    assert "class_ids" in rows[0]
    assert "DriveType" in rows[0]
    assert "Manufacturer" in rows[0]


def test_equipment_csv_rows():
    rows = parse_csv(export_equipment_csv(make_model(XML)))
    names = [r["full_name"] for r in rows]
    assert "Mine" in names
    assert "Mine.Plant" in names


def test_equipment_csv_property_value():
    rows = parse_csv(export_equipment_csv(make_model(XML)))
    plant = next(r for r in rows if r["full_name"] == "Mine.Plant")
    assert plant["DriveType"] == "Electric"


def test_equipment_csv_class_ids():
    rows = parse_csv(export_equipment_csv(make_model(XML)))
    plant = next(r for r in rows if r["full_name"] == "Mine.Plant")
    assert "Crusher" in plant["class_ids"]


def test_classes_csv_headers():
    rows = parse_csv(export_classes_csv(make_model(XML)))
    assert "name" in rows[0]
    assert "parent" in rows[0]
    assert "DriveType" in rows[0]


def test_classes_csv_rows():
    rows = parse_csv(export_classes_csv(make_model(XML)))
    names = [r["name"] for r in rows]
    assert "Crusher" in names


def test_classes_csv_property_value():
    rows = parse_csv(export_classes_csv(make_model(XML)))
    crusher = next(r for r in rows if r["name"] == "Crusher")
    assert crusher["Manufacturer"] == "ACME"


def test_returns_string():
    model = make_model(XML)
    assert isinstance(export_equipment_csv(model), str)
    assert isinstance(export_classes_csv(model), str)


def test_api_csv_equipment():
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/csv/equipment",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    rows = list(csv.DictReader(StringIO(response.text)))
    assert len(rows) > 0
    assert "full_name" in rows[0]


def test_api_csv_classes():
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/csv/classes",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    rows = list(csv.DictReader(StringIO(response.text)))
    assert len(rows) > 0
    assert "name" in rows[0]
