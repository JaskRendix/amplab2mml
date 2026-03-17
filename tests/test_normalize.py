import pytest
from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml
from app.transformers.normalize import normalize_to_xslt_semantics


def parse(xml: str):
    return etree.fromstring(xml.encode("utf-8"))


def get_equipment(model):
    return model["equipment"]


def get_classes(model):
    return model["classes"]


@pytest.mark.parametrize(
    "xml, expected_class_name, expected_parent",
    [
        (
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
            "Child.Grandchild",  # XSLT: skip first ancestor
            "Child",
        ),
        (
            """
            <Ampla>
              <ClassDefinitions>
                <ClassDefinition id="10" name="Only"/>
              </ClassDefinitions>
            </Ampla>
            """,
            "Only",  # No ancestors → unchanged
            None,
        ),
    ],
)
def test_class_name_normalization(xml, expected_class_name, expected_parent):
    root = parse(xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    classes = get_classes(model)
    assert len(classes) == 1
    cls = classes[0]

    assert cls.name == expected_class_name
    assert cls.parent == expected_parent


def test_equipment_class_id_direct_only(minimal_ampla_xml):
    root = parse(minimal_ampla_xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    eq = get_equipment(model)[0]
    assert eq.class_ids == ["Base"]  # Only direct class, no ancestors


@pytest.mark.parametrize(
    "xml, expected_full_name",
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
            "A.B.C",
        ),
        (
            """
            <Ampla>
              <Item id="1" name="A" type="Citect.Ampla.Isa95.EnterpriseFolder">
                <Item id="2" type="Citect.Ampla.Isa95.SiteFolder">
                  <Item id="3" name="C" type="Citect.Ampla.Isa95.AreaFolder"/>
                </Item>
              </Item>
            </Ampla>
            """,
            "A.C",  # middle node has no @name → skipped
        ),
    ],
)
def test_full_name_generation(xml, expected_full_name):
    root = parse(xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    eq3 = None
    for eq in get_equipment(model):
        stack = [eq]
        while stack:
            cur = stack.pop()
            if cur.id == "3":
                eq3 = cur
                break
            stack.extend(cur.children)

    assert eq3 is not None
    assert eq3.full_name == expected_full_name


@pytest.mark.parametrize(
    "item_type, expected_level",
    [
        ("Citect.Ampla.Isa95.EnterpriseFolder", "Enterprise"),
        ("Citect.Ampla.Isa95.SiteFolder", "Site"),
        ("Citect.Ampla.Isa95.AreaFolder", "Area"),
        ("Citect.Ampla.General.Server.ApplicationsFolder", "Other"),
        ("Citect.Ampla.Isa95.WorkCenter", "Other"),  # XSLT fallback
        ("Citect.Ampla.Isa95.Unit", "Other"),  # XSLT fallback
    ],
)
def test_equipment_element_level(item_type, expected_level):
    xml = f"""
    <Ampla>
      <Item id="1" name="X" type="{item_type}"/>
    </Ampla>
    """
    root = parse(xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    eq = get_equipment(model)[0]
    assert eq.level == expected_level


def test_property_inheritance_and_override():
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="10"/>
        <Property name="Class.PropA">OverrideA</Property>
      </Item>

      <ClassDefinitions>
        <ClassDefinition id="10" name="Root">
          <ClassDefinition name="Child">
            <PropertyDefinition name="PropA" type="System.String">ValueA</PropertyDefinition>
            <PropertyDefinition name="PropB" type="System.Int32">42</PropertyDefinition>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    root = parse(xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    eq = get_equipment(model)[0]
    props = {p.name: p for p in eq.properties}

    assert props["PropA"].value == "OverrideA"
    assert props["PropA"].datatype == "string"

    assert props["PropB"].value == "42"
    assert props["PropB"].datatype == "int"

    names = [p.name for p in eq.properties]
    assert names == sorted(names)


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

    root = parse(xml)
    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    cls = get_classes(model)[0]
    names = [p.name for p in cls.properties]
    assert names == ["Alpha", "Beta", "Zeta"]
