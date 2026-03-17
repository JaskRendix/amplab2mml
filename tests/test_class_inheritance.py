from lxml import etree

from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml


def test_class_inheritance_chain():
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

    # Expect hierarchical names:
    # Base
    # Base.Child
    # Base.Child.Grandchild
    base, child, grandchild = sorted(model["classes"], key=lambda c: c.name)

    assert [c.name for c in base.inheritance_chain] == ["Base"]

    assert [c.name for c in child.inheritance_chain] == ["Base", "Base.Child"]

    assert [c.name for c in grandchild.inheritance_chain] == [
        "Base",
        "Base.Child",
        "Base.Child.Grandchild",
    ]
