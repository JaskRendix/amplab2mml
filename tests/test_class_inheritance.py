from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


def test_class_inheritance_chain():
    """
    Top-level ClassDefinition with children is a grouping container —
    it is skipped in naming (XSLT get-class-name position() > 1).
    Only Child and Child.Grandchild are real classes.
    """
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Base">
          <ClassDefinition id="2" name="Child">
            <ClassDefinition id="3" name="Grandchild"/>
          </ClassDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    root = etree.fromstring(xml)
    model = transform_ampla_to_b2mml(root)

    classes = {cls.name: cls for cls in model["classes"]}
    assert set(classes) == {"Child", "Child.Grandchild"}

    assert [c.name for c in classes["Child"].inheritance_chain] == ["Child"]
    assert [c.name for c in classes["Child.Grandchild"].inheritance_chain] == [
        "Child",
        "Child.Grandchild",
    ]


def test_flat_class_is_real_class():
    """
    Top-level ClassDefinition with no children is itself the real class.
    """
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <PropertyDefinition name="PropA" type="System.String">ValueA</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    root = etree.fromstring(xml)
    model = transform_ampla_to_b2mml(root)

    classes = {cls.name: cls for cls in model["classes"]}
    assert set(classes) == {"Base"}
    assert classes["Base"].parent is None
    assert classes["Base"].properties[0].name == "PropA"
