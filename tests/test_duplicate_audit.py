from app.duplicate_audit import audit_duplicates, render_duplicate_audit


def test_duplicate_audit_clean_model(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Crusher">
          <PropertyDefinition name="Power">1000</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>

      <Item id="100"
            name="Crusher01"
            type="Citect.Ampla.Isa95.AreaFolder"/>
    </Ampla>
    """

    model = make_model(xml)
    report = audit_duplicates(model)

    assert report["errors"] == []
    assert report["warnings"] == []
    assert report["summary"]["errors"] == 0
    assert report["summary"]["warnings"] == 0


def test_duplicate_equipment_id(make_model):
    xml = """
    <Ampla>
      <Item id="100"
            name="A"
            type="Citect.Ampla.Isa95.AreaFolder"/>

      <Item id="100"
            name="B"
            type="Citect.Ampla.Isa95.AreaFolder"/>
    </Ampla>
    """

    model = make_model(xml)

    report = audit_duplicates(model)

    assert {
        "rule": "DUPLICATE_EQUIPMENT_ID",
        "id": "100",
        "count": 2,
    } in report["errors"]


def test_duplicate_equipment_full_name(make_model):
    xml = """
    <Ampla>
      <Item id="1"
            name="Crusher"
            type="Citect.Ampla.Isa95.AreaFolder"/>

      <Item id="2"
            name="Crusher"
            type="Citect.Ampla.Isa95.AreaFolder"/>
    </Ampla>
    """

    model = make_model(xml)

    report = audit_duplicates(model)

    assert {
        "rule": "DUPLICATE_EQUIPMENT_FULL_NAME",
        "name": "Crusher",
        "count": 2,
    } in report["errors"]


def test_duplicate_class_name(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Crusher"/>
        <ClassDefinition id="2" name="Crusher"/>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = audit_duplicates(model)

    assert {
        "rule": "DUPLICATE_CLASS_NAME",
        "name": "Crusher",
        "count": 2,
    } in report["errors"]


def test_duplicate_class_property(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Crusher">
          <PropertyDefinition name="Power">1000</PropertyDefinition>
          <PropertyDefinition name="Power">2000</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = audit_duplicates(model)

    assert {
        "rule": "DUPLICATE_CLASS_PROPERTY",
        "class": "Crusher",
        "property": "Power",
        "count": 2,
    } in report["warnings"]


def test_duplicate_audit_summary_counts(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Crusher">
          <PropertyDefinition name="Power">1000</PropertyDefinition>
          <PropertyDefinition name="Power">2000</PropertyDefinition>
        </ClassDefinition>

        <ClassDefinition id="2" name="Crusher"/>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = audit_duplicates(model)

    assert report["summary"]["errors"] == 1
    assert report["summary"]["warnings"] == 1


def test_duplicate_audit_rendering(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Crusher"/>
        <ClassDefinition id="2" name="Crusher"/>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    output = render_duplicate_audit(model)

    assert "Duplicate Audit" in output
    assert "Errors" in output
    assert "Warnings" in output
    assert "DUPLICATE_CLASS_NAME" in output
    assert "Crusher" in output
