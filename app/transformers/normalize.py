from app.models.properties import EquipmentProperty


def normalize_to_xslt_semantics(model, ampla_root):
    """
    Mutates the model in-place so that the output matches the XSLT exactly.
    """

    class_lookup = {cls.name: cls for cls in model["classes"]}

    for cls in model["classes"]:
        parts = cls.name.split(".")
        if len(parts) > 1:
            cls.name = ".".join(parts[1:])
            cls.parent = ".".join(parts[1:-1]) if len(parts) > 2 else None
        else:
            cls.parent = None

    def trim_class_ids(eq):
        if eq.class_ids:
            eq.class_ids = eq.class_ids[-1:]
        for child in eq.children:
            trim_class_ids(child)

    for eq in model["equipment"]:
        trim_class_ids(eq)

    xml_by_id = {n.get("id"): n for n in ampla_root.xpath("//Item")}

    def compute_full_name_from_xml(node):
        names = [anc.get("name") for anc in node.xpath("ancestor-or-self::*[@name]")]
        return ".".join(names)

    def assign_full_names(eq):
        xml_node = xml_by_id.get(eq.id)
        if xml_node is not None:
            eq.full_name = compute_full_name_from_xml(xml_node)
        for child in eq.children:
            assign_full_names(child)

    for eq in model["equipment"]:
        assign_full_names(eq)

    xslt_mapping = {
        "Citect.Ampla.Isa95.EnterpriseFolder": "Enterprise",
        "Citect.Ampla.Isa95.SiteFolder": "Site",
        "Citect.Ampla.Isa95.AreaFolder": "Area",
        "Citect.Ampla.General.Server.ApplicationsFolder": "Other",
    }

    type_by_id = {n.get("id"): n.get("type") for n in ampla_root.xpath("//Item")}

    def fix_levels(eq):
        t = type_by_id.get(eq.id)
        eq.level = xslt_mapping.get(t, "Other")
        for child in eq.children:
            fix_levels(child)

    for eq in model["equipment"]:
        fix_levels(eq)

    def merge_properties(eq):
        merged = {}

        for cid in eq.class_ids:
            if cid not in class_lookup:
                continue
            cls = class_lookup[cid]
            for ancestor in cls.inheritance_chain:
                for p in ancestor.properties:
                    merged[p.name] = EquipmentProperty(
                        name=p.name,
                        value=p.value,
                        datatype=p.datatype,
                    )

        for key, value in eq.overrides.items():
            if key.startswith("Class."):
                prop_name = key.split(".", 1)[1]
            else:
                prop_name = key

            if prop_name in merged:
                merged[prop_name].value = value
            else:
                merged[prop_name] = EquipmentProperty(
                    name=prop_name,
                    value=value,
                    datatype="string",
                )

        eq.properties = sorted(merged.values(), key=lambda p: p.name)

        for child in eq.children:
            merge_properties(child)

    for eq in model["equipment"]:
        merge_properties(eq)

    for cls in model["classes"]:
        cls.properties = sorted(cls.properties, key=lambda p: p.name)

    class_names = {cls.name for cls in model["classes"]}
    parent_names = {cls.parent for cls in model["classes"] if cls.parent}

    leaf_classes = [
        cls
        for cls in model["classes"]
        if cls.parent in class_names and cls.name not in parent_names
    ]

    if leaf_classes:
        model["classes"] = leaf_classes

    return model
