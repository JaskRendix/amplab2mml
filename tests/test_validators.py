from app.models.classes import EquipmentClass
from app.models.equipment import Equipment
from app.validators import validate_model


def test_no_warnings_on_valid_model(make_model):
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="20"/>
      </Item>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <ClassDefinition id="20" name="Child"/>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = make_model(xml)
    assert validate_model(model) == []


def test_unknown_class_reference():
    eq = Equipment(
        id="1",
        name="Mine",
        level="Enterprise",
        full_name="Mine",
        class_ids=["GhostClass"],
    )
    cls = EquipmentClass(name="RealClass", parent=None, properties=[])
    model = {"equipment": [eq], "classes": [cls], "warnings": []}

    warnings = validate_model(model)
    assert any("unknown class" in w for w in warnings)
    assert any("GhostClass" in w for w in warnings)


def test_unknown_parent_class():
    cls = EquipmentClass(name="Child", parent="NonExistent", properties=[])
    model = {"equipment": [], "classes": [cls], "warnings": []}

    warnings = validate_model(model)
    assert any("unknown parent" in w for w in warnings)
    assert any("NonExistent" in w for w in warnings)


def test_circular_inheritance():
    a = EquipmentClass(name="A", parent="B", properties=[])
    b = EquipmentClass(name="B", parent="A", properties=[])
    model = {"equipment": [], "classes": [a, b], "warnings": []}

    warnings = validate_model(model)
    assert any("circular" in w for w in warnings)


def test_warnings_in_pipeline():
    from app.pipeline import run_pipeline_from_bytes

    xml = b"""
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="20"/>
      </Item>
      <ClassDefinitions>
        <ClassDefinition id="10" name="Base">
          <ClassDefinition id="20" name="Child"/>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """
    model = run_pipeline_from_bytes(xml)
    assert "warnings" in model
    assert isinstance(model["warnings"], list)
    assert model["warnings"] == []


def test_transformer_unknown_class_warning(make_model):
    xml = """
    <Ampla>
      <Item id="1" name="X" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <ItemClassAssociation classDefinitionId="999"/>
      </Item>
    </Ampla>
    """
    model = make_model(xml)
    assert "warnings" in model
    assert len(model["warnings"]) == 1
    assert "999" in model["warnings"][0]
