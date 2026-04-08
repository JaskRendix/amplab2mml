import pytest


@pytest.mark.parametrize(
    "override_value,expected",
    [
        ("Override", "Override"),
        (None, "Default"),  # no override → inherited value
    ],
)
def test_property_merging(make_model, override_value, expected):
    override_xml = (
        f"<Property name='Class.PropA'>{override_value}</Property>"
        if override_value is not None
        else ""
    )

    xml = f"""
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="10"/>
        {override_xml}
      </Item>

      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <PropertyDefinition name="PropA" type="System.String">Default</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)
    eq = model["equipment"][0]
    props = {p.name: p.value for p in eq.properties}

    assert props["PropA"] == expected
