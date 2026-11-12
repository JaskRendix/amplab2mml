from app.inheritance_audit import build_inheritance_audit, render_inheritance_audit


def test_inheritance_audit_basic(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Base">

          <ClassDefinition id="2" name="Crusher">
            <PropertyDefinition name="Power" type="System.String">1000</PropertyDefinition>
            <PropertyDefinition name="Vendor" type="System.String">Acme</PropertyDefinition>

            <ClassDefinition id="3" name="SecondaryCrusher">
              <PropertyDefinition name="CrusherType" type="System.String">Cone</PropertyDefinition>
              <PropertyDefinition name="OperatingMode" type="System.String">Auto</PropertyDefinition>
            </ClassDefinition>

          </ClassDefinition>

        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = next(
        item
        for item in build_inheritance_audit(model)
        if item["class_name"] == "Crusher.SecondaryCrusher"
    )

    assert report["parent"] == "Crusher"

    assert report["inheritance_chain"] == [
        "Crusher",
        "Crusher.SecondaryCrusher",
    ]

    assert report["declared_properties"] == [
        "CrusherType",
        "OperatingMode",
    ]

    assert report["inherited_properties"] == [
        {"name": "Power", "origin": "Crusher"},
        {"name": "Vendor", "origin": "Crusher"},
    ]

    assert report["declared_count"] == 2
    assert report["inherited_count"] == 2


def test_inheritance_audit_nearest_ancestor_wins(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Root">
          <PropertyDefinition name="Shared" type="System.String">RootValue</PropertyDefinition>

          <ClassDefinition id="2" name="Crusher">
            <PropertyDefinition name="Shared" type="System.String">CrusherValue</PropertyDefinition>
            <PropertyDefinition name="MaxFeed" type="System.String">50</PropertyDefinition>

            <ClassDefinition id="3" name="SecondaryCrusher"/>
          </ClassDefinition>

        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = next(
        item
        for item in build_inheritance_audit(model)
        if item["class_name"] == "Crusher.SecondaryCrusher"
    )

    assert report["inherited_properties"] == [
        {"name": "MaxFeed", "origin": "Crusher"},
        {"name": "Shared", "origin": "Crusher"},
    ]

    assert report["inherited_count"] == 2


def test_inheritance_audit_local_override_not_reported_as_inherited(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Root">
          <PropertyDefinition name="Vendor" type="System.String">RootVendor</PropertyDefinition>

          <ClassDefinition id="2" name="Crusher">
            <PropertyDefinition name="Vendor" type="System.String">CrusherVendor</PropertyDefinition>

            <ClassDefinition id="3" name="SecondaryCrusher">
              <PropertyDefinition name="Vendor" type="System.String">LocalVendor</PropertyDefinition>
            </ClassDefinition>

          </ClassDefinition>

        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = next(
        item
        for item in build_inheritance_audit(model)
        if item["class_name"] == "Crusher.SecondaryCrusher"
    )

    assert report["declared_properties"] == ["Vendor"]

    assert report["inherited_properties"] == []

    assert report["declared_count"] == 1
    assert report["inherited_count"] == 0


def test_inheritance_audit_nearest_ancestor_origin(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Root">
          <PropertyDefinition name="Vendor" type="System.String">RootVendor</PropertyDefinition>

          <ClassDefinition id="2" name="Crusher">
            <PropertyDefinition name="Vendor" type="System.String">CrusherVendor</PropertyDefinition>

            <ClassDefinition id="3" name="SecondaryCrusher"/>
          </ClassDefinition>

        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = next(
        item
        for item in build_inheritance_audit(model)
        if item["class_name"] == "Crusher.SecondaryCrusher"
    )

    assert report["inherited_properties"] == [{"name": "Vendor", "origin": "Crusher"}]


def test_inheritance_audit_root_class(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Base">
          <PropertyDefinition name="PropA" type="System.String">ValueA</PropertyDefinition>
        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)

    report = next(
        item for item in build_inheritance_audit(model) if item["class_name"] == "Base"
    )

    assert report["parent"] is None

    assert report["inheritance_chain"] == ["Base"]

    assert report["declared_properties"] == ["PropA"]

    assert report["inherited_properties"] == []

    assert report["declared_count"] == 1
    assert report["inherited_count"] == 0


def test_inheritance_audit_rendering(make_model):
    xml = """
    <Ampla>
      <ClassDefinitions>
        <ClassDefinition id="1" name="Base">

          <ClassDefinition id="2" name="Crusher">
            <PropertyDefinition name="Power" type="System.String">1000</PropertyDefinition>

            <ClassDefinition id="3" name="SecondaryCrusher">
              <PropertyDefinition name="OperatingMode" type="System.String">Auto</PropertyDefinition>
            </ClassDefinition>

          </ClassDefinition>

        </ClassDefinition>
      </ClassDefinitions>
    </Ampla>
    """

    model = make_model(xml)
    output = render_inheritance_audit(model)

    assert "Class: Crusher.SecondaryCrusher" in output
    assert "Parent:" in output
    assert "Inheritance Chain:" in output
    assert "Declared Properties:" in output
    assert "Inherited Properties:" in output
    assert "Summary:" in output

    assert "OperatingMode" in output
    assert "Power <- Crusher" in output
