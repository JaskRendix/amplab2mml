import csv
from io import StringIO


def _flatten_equipment(equipment_list) -> list:
    flat = []
    stack = list(equipment_list)
    while stack:
        eq = stack.pop(0)
        flat.append(eq)
        stack = list(eq.children) + stack
    return flat


def export_equipment_csv(model: dict) -> str:
    flat = _flatten_equipment(model["equipment"])

    prop_names = []
    seen = set()
    for eq in flat:
        for p in eq.properties:
            if p.name not in seen:
                prop_names.append(p.name)
                seen.add(p.name)

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["full_name", "level", "class_ids"] + prop_names)

    for eq in flat:
        prop_map = {p.name: p.value or "" for p in eq.properties}
        writer.writerow(
            [
                eq.full_name or "",
                eq.level or "",
                ", ".join(eq.class_ids),
            ]
            + [prop_map.get(n, "") for n in prop_names]
        )

    return buf.getvalue()


def export_classes_csv(model: dict) -> str:
    classes = model["classes"]

    prop_names = []
    seen = set()
    for cls in classes:
        for p in cls.properties:
            if p.name not in seen:
                prop_names.append(p.name)
                seen.add(p.name)

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "parent"] + prop_names)

    for cls in classes:
        prop_map = {p.name: p.value or "" for p in cls.properties}
        writer.writerow(
            [
                cls.name,
                cls.parent or "",
            ]
            + [prop_map.get(n, "") for n in prop_names]
        )

    return buf.getvalue()
