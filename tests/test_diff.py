from app.diff import diff_models

BASE_XML = """
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


def test_no_diff_identical(make_model):
    model_a = make_model(BASE_XML)
    model_b = make_model(BASE_XML)
    result = diff_models(model_a, model_b)
    assert result.is_empty()


def test_equipment_added(make_model):
    changed = BASE_XML.replace(
        "</Item>\n  <ClassDefinitions>",
        """
        <Item id="3" name="Warehouse" type="Citect.Ampla.Isa95.SiteFolder"/>
      </Item>
  <ClassDefinitions>""",
    )
    result = diff_models(make_model(BASE_XML), make_model(changed))
    assert "Mine.Warehouse" in result.equipment_added
    assert result.equipment_removed == []


def test_equipment_removed(make_model):
    no_plant = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder"/>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <ClassDefinition id="20" name="Crusher">
            <PropertyDefinition name="DriveType" type="System.String">Unknown</PropertyDefinition>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    result = diff_models(make_model(BASE_XML), make_model(no_plant))
    assert "Mine.Plant" in result.equipment_removed
    assert result.equipment_added == []


def test_property_value_changed(make_model):
    changed = BASE_XML.replace(
        '<Property name="Class.DriveType">Electric</Property>',
        '<Property name="Class.DriveType">Hydraulic</Property>',
    )
    result = diff_models(make_model(BASE_XML), make_model(changed))
    assert not result.is_empty()

    plant_changes = next(
        c for c in result.equipment_properties_changed if c["equipment"] == "Mine.Plant"
    )
    drive = next(p for p in plant_changes["changed"] if p["name"] == "DriveType")

    assert drive["old"] == "Electric"
    assert drive["new"] == "Hydraulic"


def test_class_added(make_model):
    extra_class = """
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
            <ClassDefinition id="30" name="JawCrusher"/>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    result = diff_models(make_model(BASE_XML), make_model(extra_class))
    assert "Crusher.JawCrusher" in result.classes_added


def test_class_removed(make_model):
    no_crusher = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder"/>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base"/>
      </ClassDefinitions>
    </Ampla>
    """
    result = diff_models(make_model(BASE_XML), make_model(no_crusher))
    assert "Crusher" in result.classes_removed


def test_diff_text_output(make_model):
    no_plant = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder"/>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <ClassDefinition id="20" name="Crusher">
            <PropertyDefinition name="DriveType" type="System.String">Unknown</PropertyDefinition>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    result = diff_models(make_model(BASE_XML), make_model(no_plant))
    text = result.to_text()
    assert "Mine.Plant" in text
    assert text.startswith("-")


def test_diff_empty_text(make_model):
    model = make_model(BASE_XML)
    result = diff_models(model, model)
    assert result.to_text() == "No differences found."


def test_api_diff_json():
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)

    xml_a = open("tests/data/sample_ampla.xml", "rb").read()
    response = client.post(
        "/diff/json",
        files={
            "file_a": ("a.xml", xml_a, "application/xml"),
            "file_b": ("b.xml", xml_a, "application/xml"),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["equipment_added"] == []
    assert data["equipment_removed"] == []


def test_api_diff_text():
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)

    xml_a = open("tests/data/sample_ampla.xml", "rb").read()
    response = client.post(
        "/diff/text",
        files={
            "file_a": ("a.xml", xml_a, "application/xml"),
            "file_b": ("b.xml", xml_a, "application/xml"),
        },
    )
    assert response.status_code == 200
    assert response.text == "No differences found."
