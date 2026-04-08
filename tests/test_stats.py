from app.stats import compute_stats

XML = """
<Ampla>
  <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
    <Item id="2" name="Plant" type="Citect.Ampla.Isa95.SiteFolder">
      <Item id="3" name="Area" type="Citect.Ampla.Isa95.AreaFolder">
        <ItemClassAssociation classDefinitionId="20"/>
        <Property name="Class.DriveType">Electric</Property>
      </Item>
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


def test_total_equipment(make_model):
    stats = compute_stats(make_model(XML))
    assert stats.total_equipment == 3


def test_total_classes(make_model):
    stats = compute_stats(make_model(XML))
    assert stats.total_classes == 1  # only Crusher (container skipped)


def test_total_properties(make_model):
    # Area has DriveType and Manufacturer from class
    stats = compute_stats(make_model(XML))
    assert stats.total_properties == 2


def test_max_depth(make_model):
    stats = compute_stats(make_model(XML))
    assert stats.max_depth == 3


def test_no_warnings(make_model):
    stats = compute_stats(make_model(XML))
    assert stats.warnings == []


def test_warnings_included():
    from app.pipeline import run_pipeline_from_bytes

    xml = b"""
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder"/>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <ClassDefinition id="20" name="Crusher"/>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = run_pipeline_from_bytes(xml)
    stats = compute_stats(model)
    assert isinstance(stats.warnings, list)


def test_to_dict(make_model):
    stats = compute_stats(make_model(XML))
    d = stats.to_dict()
    assert "total_equipment" in d
    assert "total_classes" in d
    assert "total_properties" in d
    assert "max_depth" in d
    assert "warnings" in d


def test_to_text(make_model):
    stats = compute_stats(make_model(XML))
    text = stats.to_text()
    assert "Equipment nodes" in text
    assert "Classes" in text
    assert "Max depth" in text
    assert "Warnings" in text


def test_api_stats():
    from fastapi.testclient import TestClient

    from app.api import app

    client = TestClient(app)
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/stats",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_equipment" in data
    assert "max_depth" in data


def test_cli_stats():
    import subprocess

    result = subprocess.run(
        ["b2mml", "stats", "tests/data/sample_ampla.xml"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Equipment nodes" in result.stdout
