def test_full_name_generation_nested(make_model):
    xml = """
    <Ampla>
      <Item id="1" name="Mine" type="Citect.Ampla.Isa95.EnterpriseFolder">
        <Item id="2" name="Plant1" type="Citect.Ampla.Isa95.SiteFolder">
          <Item id="3" name="AreaA" type="Citect.Ampla.Isa95.AreaFolder"/>
        </Item>
      </Item>
    </Ampla>
    """

    model = make_model(xml)

    mine = model["equipment"][0]
    plant = mine.children[0]
    area = plant.children[0]

    assert mine.full_name == "Mine"
    assert plant.full_name == "Mine.Plant1"
    assert area.full_name == "Mine.Plant1.AreaA"
