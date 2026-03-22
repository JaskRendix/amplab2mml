from datetime import UTC, datetime

from lxml import etree

from app.models.properties import EquipmentProperty

NS = "http://www.wbf.org/xml/b2mml-v0400"


def build_b2mml_xml(model):
    root = etree.Element(
        "ShowEquipmentInformation",
        attrib={"releaseID": ""},
        nsmap={
            None: NS,
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsd": "http://www.w3.org/2001/XMLSchema",
        },
    )

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

    e.append(
        build_equipment_property_xml(
            EquipmentProperty(name="Ampla.Name", value=eq.name, datatype="string")
        )
    )

    for prop in eq.properties:
        e.append(build_equipment_property_xml(prop))

    for child in eq.children:
        e.append(build_equipment_xml(child))

    for cid in eq.class_ids:
        etree.SubElement(e, "EquipmentClassID").text = cid

    loc = etree.SubElement(e, "Location")
    etree.SubElement(loc, "EquipmentID").text = eq.id
    etree.SubElement(loc, "EquipmentElementLevel").text = eq.level

    return e


def build_equipment_property_xml(prop):
    ep = etree.Element("EquipmentProperty")
    etree.SubElement(ep, "ID").text = prop.name
    val = etree.SubElement(ep, "Value")
    etree.SubElement(val, "ValueString").text = (
        prop.value if prop.value is not None else ""
    )
    etree.SubElement(val, "DataType").text = prop.datatype
    etree.SubElement(val, "UnitOfMeasure")
    return ep


def build_class_xml(cls):
    c = etree.Element("EquipmentClass")
    etree.SubElement(c, "ID").text = (
        cls.name
    )  # full dotted name e.g. "Crusher.JawCrusher"

    if cls.parent:
        parent_prop = etree.SubElement(c, "EquipmentClassProperty")
        etree.SubElement(parent_prop, "ID").text = "Ampla.Parent"
        etree.SubElement(parent_prop, "Description").text = "Ampla Reserved property"
        val = etree.SubElement(parent_prop, "Value")
        etree.SubElement(val, "ValueString").text = cls.parent
        etree.SubElement(val, "DataType").text = "string"
        etree.SubElement(val, "UnitOfMeasure")

    name_prop = etree.SubElement(c, "EquipmentClassProperty")
    etree.SubElement(name_prop, "ID").text = "Ampla.Name"
    etree.SubElement(name_prop, "Description").text = "Ampla Reserved property"
    val = etree.SubElement(name_prop, "Value")
    # Ampla.Name is the short segment only, not the full dotted name
    etree.SubElement(val, "ValueString").text = cls.name.split(".")[-1]
    etree.SubElement(val, "DataType").text = "string"
    etree.SubElement(val, "UnitOfMeasure")

    for prop in cls.properties:
        c.append(build_class_property_xml(prop))

    return c


def build_class_property_xml(prop):
    cp = etree.Element("EquipmentClassProperty")
    etree.SubElement(cp, "ID").text = prop.name
    etree.SubElement(cp, "Description").text = prop.description or ""
    val = etree.SubElement(cp, "Value")
    etree.SubElement(val, "ValueString").text = prop.value or ""
    etree.SubElement(val, "DataType").text = prop.datatype
    etree.SubElement(val, "UnitOfMeasure")
    return cp
