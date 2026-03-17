import pytest


@pytest.fixture
def minimal_ampla_xml():
    return """
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
