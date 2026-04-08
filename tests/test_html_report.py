import subprocess

from fastapi.testclient import TestClient

from app.api import app
from app.html_report import export_to_html
from app.models.equipment import Equipment

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


def test_returns_string(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert isinstance(result, str)
    assert len(result) > 0


def test_is_valid_html(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "<!DOCTYPE html>" in result
    assert "</html>" in result


def test_contains_equipment_names(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "Mine" in result
    assert "Plant" in result


def test_contains_class_names(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "Crusher" in result


def test_contains_property_values(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "Electric" in result
    assert "ACME" in result


def test_contains_stats(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "equipment nodes" in result
    assert "classes" in result
    assert "max depth" in result


def test_warnings_section_absent_when_no_warnings(make_model):
    model = make_model(XML)
    result = export_to_html(model)
    assert "Warnings" not in result


def test_warnings_section_present():
    model = {
        "equipment": [],
        "classes": [],
        "warnings": ["Equipment 'X' references unknown class 'Y'"],
    }
    result = export_to_html(model)
    assert "Warnings" in result
    assert "unknown class" in result


def test_xss_escaping():
    eq = Equipment(
        id="1",
        name="<script>alert(1)</script>",
        level="Enterprise",
        full_name="<script>alert(1)</script>",
    )
    model = {"equipment": [eq], "classes": [], "warnings": []}
    result = export_to_html(model)
    assert "<script>alert(1)</script>" not in result
    assert "&lt;script&gt;" in result


def test_api_html_report():
    client = TestClient(app)
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/html",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "AcmeMining" in response.text


def test_cli_html(tmp_path):
    input_file = "tests/data/sample_ampla.xml"
    output_file = tmp_path / "report.html"
    result = subprocess.run(
        ["b2mml", "html", input_file, str(output_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "<!DOCTYPE html>" in content
    assert "AcmeMining" in content
