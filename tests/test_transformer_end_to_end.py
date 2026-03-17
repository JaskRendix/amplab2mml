from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


def test_end_to_end_transformer():
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="10"/>
      </Item>

      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <PropertyDefinition name="PropA" type="System.String">ValueA</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    root = etree.fromstring(xml)
    model = transform_ampla_to_b2mml(root)

    eq = model["equipment"][0]

    assert eq.full_name == "Mine"
    assert eq.class_ids == ["Base"]
    assert len(eq.properties) == 1
    assert eq.properties[0].name == "PropA"
    assert eq.properties[0].value == "ValueA"
