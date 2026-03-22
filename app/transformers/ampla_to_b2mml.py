from app.models.classes import EquipmentClass
from app.models.equipment import Equipment
from app.models.properties import ClassProperty, EquipmentProperty

# ISA-95 / Ampla type → B2MML EquipmentElementLevel.
# Types not listed here are accepted but mapped to "Other" (XSLT fallback).
_LEVEL_MAP = {
    "Citect.Ampla.Isa95.EnterpriseFolder": "Enterprise",
    "Citect.Ampla.Isa95.SiteFolder": "Site",
    "Citect.Ampla.Isa95.AreaFolder": "Area",
    "Citect.Ampla.General.Server.ApplicationsFolder": "Other",
}


def transform_ampla_to_b2mml(root):
    # 1. Parse equipment tree
    equipment = [
        eq
        for item in root.xpath("/Ampla/Item")
        for eq in [_convert_item(item)]
        if eq is not None
    ]

    # 2. Parse class hierarchy.
    #    The XSLT skips the top-level ClassDefinition as a container when it
    #    has ClassDefinition children (get-class-name uses position() > 1).
    #    When a top-level node has no children it IS the real class.
    classes = []
    for container in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
        children = container.xpath("ClassDefinition")
        if children:
            for child in children:
                classes.extend(_extract_classes(child, parent_full_name=None))
        else:
            classes.extend(_extract_classes(container, parent_full_name=None))

    # 3. Build lookup: every ClassDefinition @id → its B2MML class name
    class_id_lookup = _build_class_id_lookup(root)

    # 4. Resolve raw XML IDs → class names on every equipment node
    for eq in equipment:
        _resolve_class_ids(eq, class_id_lookup)

    # 5. Compute dotted full names, skipping nameless nodes
    _compute_full_names(equipment, parent_full_name=None)

    # 6. Build inheritance chains (needed before property merge)
    _compute_class_inheritance(classes)

    # 7. Merge class properties into equipment with override handling
    _merge_properties(equipment, classes)

    # 8. Sort class properties alphabetically (XSLT <xsl:sort select="@name"/>)
    for cls in classes:
        cls.properties = sorted(cls.properties, key=lambda p: p.name)

    return {"equipment": equipment, "classes": classes}


def _extract_classes(node, parent_full_name):
    name = node.get("name")
    full_name = name if parent_full_name is None else f"{parent_full_name}.{name}"

    props = [
        ClassProperty(
            name=p.get("name"),
            description=p.get("description"),
            value=p.text,
            datatype=_translate_datatype(p.get("type")),
        )
        for p in node.xpath("PropertyDefinition")
    ]

    cls = EquipmentClass(
        name=full_name,
        parent=parent_full_name,
        properties=props,
    )

    result = [cls]
    for child in node.xpath("ClassDefinition"):
        result.extend(_extract_classes(child, full_name))

    return result


def _build_class_id_lookup(root):
    """
    Map every ClassDefinition @id to its B2MML class name.
    Mirrors the container-vs-real-class logic from _extract_classes exactly.
    """
    lookup = {}

    def _walk(node, parent_full_name):
        name = node.get("name")
        full_name = name if parent_full_name is None else f"{parent_full_name}.{name}"
        node_id = node.get("id")
        if node_id:
            lookup[node_id] = full_name
        for child in node.xpath("ClassDefinition"):
            _walk(child, full_name)

    for container in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
        children = container.xpath("ClassDefinition")
        if children:
            for child in children:
                _walk(child, parent_full_name=None)
            # defensive: index the container's own @id to its bare name
            container_id = container.get("id")
            if container_id and container_id not in lookup:
                lookup[container_id] = container.get("name")
        else:
            _walk(container, parent_full_name=None)

    return lookup


def _convert_item(node):
    item_type = node.get("type")
    # Fall back to "Other" for any type not explicitly listed, matching XSLT.
    level = _LEVEL_MAP.get(item_type, "Other")

    children = [c for c in (_convert_item(n) for n in node.xpath("Item")) if c]
    class_ids = [a.get("classDefinitionId") for a in node.xpath("ItemClassAssociation")]
    overrides = {p.get("name"): p.text for p in node.xpath("Property")}

    return Equipment(
        id=node.get("id"),
        name=node.get("name") or "",
        level=level,
        children=children,
        properties=[],
        class_ids=class_ids,
        overrides=overrides,
    )


def _resolve_class_ids(eq, lookup):
    eq.class_ids = [lookup[cid] for cid in eq.class_ids if cid in lookup]
    for child in eq.children:
        _resolve_class_ids(child, lookup)


def _compute_full_names(equipment_list, parent_full_name):
    for eq in equipment_list:
        if eq.name:
            eq.full_name = (
                f"{parent_full_name}.{eq.name}" if parent_full_name else eq.name
            )
            next_parent = eq.full_name
        else:
            eq.full_name = parent_full_name or ""
            next_parent = parent_full_name

        _compute_full_names(eq.children, next_parent)


def _compute_class_inheritance(classes):
    lookup = {cls.name: cls for cls in classes}

    for cls in classes:
        chain = []
        current = cls
        while current:
            chain.append(current)
            current = lookup.get(current.parent) if current.parent else None
        cls.inheritance_chain = chain[::-1]


def _merge_properties(equipment, classes):
    class_lookup = {cls.name: cls for cls in classes}

    def _merge_for(eq):
        merged: dict[str, EquipmentProperty] = {}

        for class_name in eq.class_ids:
            cls = class_lookup.get(class_name)
            if not cls:
                continue
            for ancestor in cls.inheritance_chain:
                for prop in ancestor.properties:
                    merged[prop.name] = EquipmentProperty(
                        name=prop.name, value=prop.value, datatype=prop.datatype
                    )

        for key, value in eq.overrides.items():
            prop_name = key.split(".", 1)[1] if key.startswith("Class.") else key
            if prop_name in merged:
                merged[prop_name].value = value
            else:
                merged[prop_name] = EquipmentProperty(
                    name=prop_name, value=value, datatype="string"
                )

        eq.properties = sorted(merged.values(), key=lambda p: p.name)

        for child in eq.children:
            _merge_for(child)

    for eq in equipment:
        _merge_for(eq)


def _translate_datatype(dt):
    if dt == "System.String":
        return "string"
    if dt == "System.Int32":
        return "int"
    return "string"
