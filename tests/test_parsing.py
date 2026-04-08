import pytest


@pytest.mark.parametrize(
    "xml,expected_name,expected_level",
    [
        (
            """
        <Ampla>
          <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder"/>
        </Ampla>
        """,
            "Mine",
            "Enterprise",
        ),
        (
            """
        <Ampla>
          <Item id="2" name="Plant1" type="Citect.Ampla.Isa95.SiteFolder"/>
        </Ampla>
        """,
            "Plant1",
            "Site",
        ),
    ],
)
def test_basic_parsing(make_model, xml, expected_name, expected_level):
    model = make_model(xml)

    eq = model["equipment"][0]
    assert eq.name == expected_name
    assert eq.level == expected_level
    assert eq.children == []


def test_class_property_datatype_translation(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <PropertyDefinition name="A" type="System.String">x</PropertyDefinition>
          <PropertyDefinition name="B" type="System.Int32">1</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = make_model(xml)
    props = {p.name: p.datatype for p in model["classes"][0].properties}
    assert props["A"] == "string"
    assert props["B"] == "int"


def test_empty_ampla_document(make_model):
    xml = "<Ampla></Ampla>"
    model = make_model(xml)
    assert model["equipment"] == []
    assert model["classes"] == []
