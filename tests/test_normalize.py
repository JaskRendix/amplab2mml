"""
Replaces test_normalize.py entirely.
All assertions are against transform_ampla_to_b2mml directly —
normalize_to_xslt_semantics no longer exists.
"""

import pytest
from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


def parse(xml: str):
    return etree.fromstring(xml.encode("utf-8"))


@pytest.mark.parametrize(
    "xml, expected_names, expected_parents",
    [
        (
            # container with children → container skipped, children are real classes
            """
        <Ampla>
          <ClassDefinitions>
            <ClassDefinition id="10" name="Root">
              <ClassDefinition name="Child">
                <ClassDefinition name="Grandchild"/>
              </ClassDefinition>
            </ClassDefinition>
          </ClassDefinitions>
        </Ampla>
        """,
            {"Child", "Child.Grandchild"},
            {"Child": None, "Child.Grandchild": "Child"},
        ),
        (
            # flat class → itself is the real class
            """
        <Ampla>
          <ClassDefinitions>
            <ClassDefinition id="10" name="Only"/>
          </ClassDefinitions>
        </Ampla>
        """,
            {"Only"},
            {"Only": None},
        ),
    ],
)
def test_class_naming(xml, expected_names, expected_parents):
    model = transform_ampla_to_b2mml(parse(xml))
    classes = {cls.name: cls for cls in model["classes"]}
    assert set(classes) == expected_names
    for name, expected_parent in expected_parents.items():
        assert classes[name].parent == expected_parent


def test_equipment_class_id_flat(minimal_ampla_xml):
    """Flat class: equipment resolves to the class name directly."""
    model = transform_ampla_to_b2mml(parse(minimal_ampla_xml))
    eq = model["equipment"][0]
    assert eq.class_ids == ["Base"]


def test_equipment_class_id_child():
    """Equipment referencing a child class ID resolves to the child name."""
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="20"/>
      </Item>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Root">
          <ClassDefinition id="20" name="Child"/>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = transform_ampla_to_b2mml(parse(xml))
    eq = model["equipment"][0]
    assert eq.class_ids == ["Child"]


@pytest.mark.parametrize(
    "xml, target_id, expected_full_name",
    [
        (
            """
        <Ampla>
          <Item id="1" name="A" type="Citect.Ampla.Isa95.EnterpriseFolder">
            <Item id="2" name="B" type="Citect.Ampla.Isa95.SiteFolder">
              <Item id="3" name="C" type="Citect.Ampla.Isa95.AreaFolder"/>
            </Item>
          </Item>
        </Ampla>
        """,
            "3",
            "A.B.C",
        ),
        (
            # nameless middle node → skipped in full name
            """
        <Ampla>
          <Item id="1" name="A" type="Citect.Ampla.Isa95.EnterpriseFolder">
            <Item id="2" type="Citect.Ampla.Isa95.SiteFolder">
              <Item id="3" name="C" type="Citect.Ampla.Isa95.AreaFolder"/>
            </Item>
          </Item>
        </Ampla>
        """,
            "3",
            "A.C",
        ),
    ],
)
def test_full_name_generation(xml, target_id, expected_full_name):
    model = transform_ampla_to_b2mml(parse(xml))

    def find(nodes):
        for eq in nodes:
            if eq.id == target_id:
                return eq
            found = find(eq.children)
            if found:
                return found

    eq = find(model["equipment"])
    assert eq is not None
    assert eq.full_name == expected_full_name


@pytest.mark.parametrize(
    "item_type, expected_level",
    [
        ("Citect.Ampla.Isa95.EnterpriseFolder", "Enterprise"),
        ("Citect.Ampla.Isa95.SiteFolder", "Site"),
        ("Citect.Ampla.Isa95.AreaFolder", "Area"),
        ("Citect.Ampla.General.Server.ApplicationsFolder", "Other"),
        ("Citect.Ampla.Isa95.WorkCenter", "Other"),  # unmapped → Other
        ("Citect.Ampla.Isa95.Unit", "Other"),  # unmapped → Other
    ],
)
def test_equipment_element_level(item_type, expected_level):
    xml = f'<Ampla><Item id="1" name="X" type="{item_type}"/></Ampla>'
    model = transform_ampla_to_b2mml(parse(xml))
    assert model["equipment"][0].level == expected_level


def test_property_inheritance_and_override():
    """
    Equipment references the child class by its own @id.
    Properties from the child are inherited; Class.PropA is overridden.
    """
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="20"/>
        <Property name="Class.PropA">OverrideA</Property>
      </Item>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Root">
          <ClassDefinition id="20" name="Child">
            <PropertyDefinition name="PropA" type="System.String">ValueA</PropertyDefinition>
            <PropertyDefinition name="PropB" type="System.Int32">42</PropertyDefinition>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = transform_ampla_to_b2mml(parse(xml))
    eq = model["equipment"][0]
    props = {p.name: p for p in eq.properties}

    assert props["PropA"].value == "OverrideA"
    assert props["PropA"].datatype == "string"
    assert props["PropB"].value == "42"
    assert props["PropB"].datatype == "int"
    assert [p.name for p in eq.properties] == sorted(p.name for p in eq.properties)


def test_class_property_sorting():
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Root">
          <PropertyDefinition name="Zeta" type="System.String">Z</PropertyDefinition>
          <PropertyDefinition name="Alpha" type="System.String">A</PropertyDefinition>
          <PropertyDefinition name="Beta" type="System.String">B</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = transform_ampla_to_b2mml(parse(xml))
    cls = model["classes"][0]
    assert [p.name for p in cls.properties] == ["Alpha", "Beta", "Zeta"]
