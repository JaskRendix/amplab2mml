import pytest
from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


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
def test_basic_parsing(xml, expected_name, expected_level):
    root = etree.fromstring(xml)
    model = transform_ampla_to_b2mml(root)

    eq = model["equipment"][0]
    assert eq.name == expected_name
    assert eq.level == expected_level
    assert eq.children == []
