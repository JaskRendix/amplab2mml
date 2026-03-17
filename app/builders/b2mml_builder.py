from datetime import UTC, datetime

from lxml import etree

NS = "http://www.wbf.org/xml/b2mml-v0400"


def build_b2mml_xml(model):
    root = etree.Element("ShowEquipmentInformation", nsmap={None: NS})

    app_area = etree.SubElement(root, "ApplicationArea")
    creation = etree.SubElement(app_area, "CreationDateTime")
    creation.text = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    data_area = etree.SubElement(root, "DataArea")
    etree.SubElement(data_area, "Show")

    eq_info = etree.SubElement(data_area, "EquipmentInformation")

    published = etree.SubElement(eq_info, "PublishedDate")
    published.text = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    for eq in model["equipment"]:
        eq_info.append(build_equipment_xml(eq))

    for cls in model["classes"]:
        eq_info.append(build_class_xml(cls))

    return etree.tostring(root, pretty_print=True, encoding="unicode")


def build_equipment_xml(eq):
    e = etree.Element("Equipment")

    id_el = etree.SubElement(e, "ID")
    id_el.set("schemeName", "Fullname")
    id_el.text = eq.full_name

    for prop in eq.properties:
        e.append(build_equipment_property_xml(prop))

    for cid in eq.class_ids:
        cid_el = etree.SubElement(e, "EquipmentClassID")
        cid_el.text = cid

    for child in eq.children:
        e.append(build_equipment_xml(child))

    loc = etree.SubElement(e, "Location")
    loc_id = etree.SubElement(loc, "EquipmentID")
    loc_id.text = eq.id

    level = etree.SubElement(loc, "EquipmentElementLevel")
    level.text = eq.level

    return e


def build_equipment_property_xml(prop):
    ep = etree.Element("EquipmentProperty")

    id_el = etree.SubElement(ep, "ID")
    id_el.text = prop.name

    val = etree.SubElement(ep, "Value")

    vs = etree.SubElement(val, "ValueString")
    vs.text = prop.value if prop.value is not None else ""

    dt = etree.SubElement(val, "DataType")
    dt.text = prop.datatype

    etree.SubElement(val, "UnitOfMeasure")

    return ep


def build_class_xml(cls):
    c = etree.Element("EquipmentClass")

    id_el = etree.SubElement(c, "ID")
    id_el.text = cls.name if not cls.parent else f"{cls.parent}.{cls.name}"

    if cls.parent:
        parent_prop = etree.SubElement(c, "EquipmentClassProperty")
        pid = etree.SubElement(parent_prop, "ID")
        pid.text = "Ampla.Parent"

        desc = etree.SubElement(parent_prop, "Description")
        desc.text = "Ampla Reserved property"

        val = etree.SubElement(parent_prop, "Value")
        vs = etree.SubElement(val, "ValueString")
        vs.text = cls.parent

        dt = etree.SubElement(val, "DataType")
        dt.text = "string"

        etree.SubElement(val, "UnitOfMeasure")

    name_prop = etree.SubElement(c, "EquipmentClassProperty")
    nid = etree.SubElement(name_prop, "ID")
    nid.text = "Ampla.Name"

    desc = etree.SubElement(name_prop, "Description")
    desc.text = "Ampla Reserved property"

    val = etree.SubElement(name_prop, "Value")
    vs = etree.SubElement(val, "ValueString")
    vs.text = cls.name

    dt = etree.SubElement(val, "DataType")
    dt.text = "string"

    etree.SubElement(val, "UnitOfMeasure")

    for prop in cls.properties:
        c.append(build_class_property_xml(prop))

    return c


def build_class_property_xml(prop):
    cp = etree.Element("EquipmentClassProperty")

    id_el = etree.SubElement(cp, "ID")
    id_el.text = prop.name

    desc = etree.SubElement(cp, "Description")
    desc.text = prop.description or ""

    val = etree.SubElement(cp, "Value")

    vs = etree.SubElement(val, "ValueString")
    vs.text = prop.value or ""

    dt = etree.SubElement(val, "DataType")
    dt.text = prop.datatype

    etree.SubElement(val, "UnitOfMeasure")

    return cp
