import pytest
from lxml import etree

from app.transformers.ampla_to_b2mml import AmplaTransformer


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


@pytest.fixture
def transformer():
    """Provides a default AmplaTransformer instance."""
    return AmplaTransformer(config_path=None)


@pytest.fixture
def make_model(transformer):
    """Parses XML and returns the transformed model."""

    def _make(xml: str):
        root = etree.fromstring(xml.encode("utf-8"))
        return transformer.transform(root)

    return _make
