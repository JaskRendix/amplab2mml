from lxml import etree

from app.models.classes import EquipmentClass
from app.models.equipment import Equipment
from app.models.properties import ClassProperty, EquipmentProperty


def transform_ampla_to_b2mml(root):
    equipment = []
    classes = []

    for item in root.xpath("/Ampla/Item"):
        eq = convert_item_to_equipment(item)
        if eq:
            equipment.append(eq)

    classes = []
    for node in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
        classes.extend(extract_classes(node))

    class_id_lookup = build_class_id_lookup(root)
    class_lookup = {cls.name: cls for cls in classes}
    compute_class_inheritance(classes)

    for eq in equipment:
        resolve_class_ids(eq, class_id_lookup, class_lookup)

    compute_full_names(equipment)
    merge_properties_into_equipment(equipment, classes)

    return {"equipment": equipment, "classes": classes}


def extract_classes(node, parent_full_name=None):
    """
    Recursively build EquipmentClass objects from ClassDefinition hierarchy.
    """
    name = node.get("name")

    full_name = name if parent_full_name is None else f"{parent_full_name}.{name}"

    props = []
    for p in node.xpath("PropertyDefinition"):
        props.append(
            ClassProperty(
                name=p.get("name"),
                description=p.get("description"),
                value=p.text,
                datatype=translate_datatype(p.get("type")),
            )
        )

    cls = EquipmentClass(
        name=full_name,
        parent=parent_full_name,
        properties=props,
    )

    classes = [cls]

    for child in node.xpath("ClassDefinition"):
        classes.extend(extract_classes(child, full_name))

    return classes


def convert_item_to_equipment(node):
    item_type = node.get("type")

    mapping = {
        # ISA‑95 hierarchy levels
        "Citect.Ampla.Isa95.EnterpriseFolder": "Enterprise",
        "Citect.Ampla.Isa95.SiteFolder": "Site",
        "Citect.Ampla.Isa95.AreaFolder": "Area",
        "Citect.Ampla.Isa95.WorkCenter": "WorkCenter",
        "Citect.Ampla.Isa95.WorkUnit": "WorkUnit",
        "Citect.Ampla.Isa95.Equipment": "Equipment",
        # Optional: common Ampla container types
        "Citect.Ampla.General.Server.ApplicationsFolder": "Other",
        "Citect.Ampla.General.Server.EquipmentFolder": "EquipmentFolder",
        # Optional: ISA‑95 production types (if your system uses them)
        "Citect.Ampla.Isa95.ProcessCell": "ProcessCell",
        "Citect.Ampla.Isa95.Unit": "Unit",
        "Citect.Ampla.Isa95.ProductionLine": "ProductionLine",
    }

    if item_type not in mapping:
        return None

    children = [convert_item_to_equipment(c) for c in node.xpath("Item")]
    children = [c for c in children if c is not None]
    class_ids = [
        assoc.get("classDefinitionId") for assoc in node.xpath("ItemClassAssociation")
    ]
    overrides = {prop.get("name"): prop.text for prop in node.xpath("Property")}

    return Equipment(
        id=node.get("id"),
        name=node.get("name") or "",
        level=mapping[item_type],
        children=children,
        properties=[],
        class_ids=class_ids,
        overrides=overrides,
    )


def translate_datatype(dt):
    if dt == "System.String":
        return "string"
    if dt == "System.Int32":
        return "int"
    return "string"


def compute_full_names(equipment_list, parent_full_name=None):
    for eq in equipment_list:
        if parent_full_name:
            eq.full_name = f"{parent_full_name}.{eq.name}"
        else:
            eq.full_name = eq.name

        compute_full_names(eq.children, eq.full_name)


def build_class_lookup(classes):
    return {cls.name: cls for cls in classes}


def compute_class_inheritance(classes):
    lookup = build_class_lookup(classes)

    for cls in classes:
        chain = []
        current = cls

        while current:
            chain.append(current)
            if current.parent and current.parent in lookup:
                current = lookup[current.parent]
            else:
                current = None

        cls.inheritance_chain = chain[::-1]


def build_class_id_lookup(root):
    """
    Map ClassDefinition @id to the most specific descendant class name,
    matching the XSLT get-class-name behavior.
    """
    lookup = {}

    for node in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
        class_id = node.get("id")
        if not class_id:
            continue

        current = node
        name_parts = [current.get("name")]

        child = current.find("ClassDefinition")
        while child is not None:
            name_parts.append(child.get("name"))
            current = child
            child = current.find("ClassDefinition")

        full_name = ".".join(name_parts)
        lookup[class_id] = full_name

    return lookup


def resolve_class_ids(eq, lookup, class_lookup):
    eq.class_ids = [lookup[cid] for cid in eq.class_ids if cid in lookup]

    for child in eq.children:
        resolve_class_ids(child, lookup, class_lookup)


def merge_properties_into_equipment(equipment, classes):
    class_lookup = {cls.name: cls for cls in classes}

    def merge_for(eq):
        merged = {}

        for class_name in eq.class_ids:
            if class_name not in class_lookup:
                continue

            cls = class_lookup[class_name]

            for ancestor in cls.inheritance_chain:
                for prop in ancestor.properties:
                    merged[prop.name] = EquipmentProperty(
                        name=prop.name, value=prop.value, datatype=prop.datatype
                    )

        for key, value in eq.overrides.items():
            if "." in key:
                _, prop_name = key.split(".", 1)
            else:
                prop_name = key

            if prop_name in merged:
                merged[prop_name].value = value
            else:
                merged[prop_name] = EquipmentProperty(
                    name=prop_name, value=value, datatype="string"
                )

        eq.properties = list(merged.values())

        for child in eq.children:
            merge_for(child)

    for eq in equipment:
        merge_for(eq)
