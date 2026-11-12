def build_inheritance_audit(model: dict) -> list[dict]:
    report: list[dict] = []

    for cls in model.get("classes", []):
        declared = [
            p.name for p in sorted(cls.properties, key=lambda p: p.name) if p.name
        ]
        declared_set = set(declared)

        # Mirror _merge_properties() inheritance behavior:
        # later ancestors overwrite earlier ones.
        inherited: dict[str, str] = {}

        for ancestor in cls.inheritance_chain[:-1]:
            for prop in ancestor.properties:
                name = getattr(prop, "name", None)

                if not name:
                    continue

                if name in declared_set:
                    continue

                inherited[name] = ancestor.name

        report.append(
            {
                "class_name": cls.name,
                "parent": cls.parent,
                "inheritance_chain": [c.name for c in cls.inheritance_chain],
                "declared_properties": declared,
                "inherited_properties": [
                    {"name": name, "origin": origin}
                    for name, origin in sorted(inherited.items())
                ],
                "declared_count": len(declared),
                "inherited_count": len(inherited),
            }
        )

    return report


def render_inheritance_audit(model: dict) -> str:
    lines: list[str] = []

    for item in build_inheritance_audit(model):
        lines.append(f"Class: {item['class_name']}")
        lines.append("")

        lines.append("Parent:")
        lines.append(f"  {item['parent']}" if item["parent"] else "  <none>")
        lines.append("")

        lines.append("Inheritance Chain:")
        if item["inheritance_chain"]:
            for name in item["inheritance_chain"]:
                lines.append(f"  {name}")
        else:
            lines.append("  <none>")
        lines.append("")

        lines.append("Declared Properties:")
        if item["declared_properties"]:
            for name in item["declared_properties"]:
                lines.append(f"  {name}")
        else:
            lines.append("  <none>")
        lines.append("")

        lines.append("Inherited Properties:")
        if item["inherited_properties"]:
            for prop in item["inherited_properties"]:
                lines.append(f"  {prop['name']} <- {prop['origin']}")
        else:
            lines.append("  <none>")
        lines.append("")

        lines.append("Summary:")
        lines.append(f"  Declared: {item['declared_count']}")
        lines.append(f"  Inherited: {item['inherited_count']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
