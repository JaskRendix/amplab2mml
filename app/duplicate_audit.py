from collections import Counter
from typing import Any


def _walk_equipment(nodes):
    for eq in nodes:
        yield eq
        yield from _walk_equipment(eq.children)


def audit_duplicates(model: dict[str, Any]) -> dict[str, Any]:
    """
    Audits the transformed model for duplicate identifiers and names.

    Rules:

    ERROR:
      - DUPLICATE_EQUIPMENT_FULL_NAME
      - DUPLICATE_EQUIPMENT_ID
      - DUPLICATE_CLASS_NAME

    WARNING:
      - DUPLICATE_CLASS_PROPERTY
    """
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    equipment = list(_walk_equipment(model.get("equipment", [])))
    classes = model.get("classes", [])

    # ------------------------------------------------------------------
    # Rule 1: Duplicate equipment full name
    # ------------------------------------------------------------------
    full_names = [eq.full_name for eq in equipment if eq.full_name]

    for name, count in Counter(full_names).items():
        if count > 1:
            errors.append(
                {
                    "rule": "DUPLICATE_EQUIPMENT_FULL_NAME",
                    "name": name,
                    "count": count,
                }
            )

    # ------------------------------------------------------------------
    # Rule 2: Duplicate equipment ID
    # ------------------------------------------------------------------
    ids = [eq.id for eq in equipment if eq.id]

    for equipment_id, count in Counter(ids).items():
        if count > 1:
            errors.append(
                {
                    "rule": "DUPLICATE_EQUIPMENT_ID",
                    "id": equipment_id,
                    "count": count,
                }
            )

    # ------------------------------------------------------------------
    # Rule 3: Duplicate class name
    # ------------------------------------------------------------------
    class_names = [cls.name for cls in classes if cls.name]

    for name, count in Counter(class_names).items():
        if count > 1:
            errors.append(
                {
                    "rule": "DUPLICATE_CLASS_NAME",
                    "name": name,
                    "count": count,
                }
            )

    # ------------------------------------------------------------------
    # Rule 4: Duplicate property name within same class
    # ------------------------------------------------------------------
    for cls in classes:
        property_names = [prop.name for prop in cls.properties if prop.name]

        for prop_name, count in Counter(property_names).items():
            if count > 1:
                warnings.append(
                    {
                        "rule": "DUPLICATE_CLASS_PROPERTY",
                        "class": cls.name,
                        "property": prop_name,
                        "count": count,
                    }
                )

    errors.sort(key=lambda e: (e["rule"], str(e.get("name", e.get("id", "")))))
    warnings.sort(
        key=lambda w: (
            w["rule"],
            str(w.get("class", "")),
            str(w.get("property", "")),
        )
    )

    return {
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def render_duplicate_audit(model: dict[str, Any]) -> str:
    report = audit_duplicates(model)

    lines: list[str] = []

    lines.append("Duplicate Audit")
    lines.append("")

    lines.append("Errors")
    lines.append("======")

    if report["errors"]:
        for error in report["errors"]:
            lines.append(error["rule"])

            if "name" in error:
                lines.append(f"  Name: {error['name']}")

            if "id" in error:
                lines.append(f"  ID: {error['id']}")

            lines.append(f"  Count: {error['count']}")
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    lines.append("Warnings")
    lines.append("========")

    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(warning["rule"])
            lines.append(f"  Class: {warning['class']}")
            lines.append(f"  Property: {warning['property']}")
            lines.append(f"  Count: {warning['count']}")
            lines.append("")
    else:
        lines.append("None")
        lines.append("")

    lines.append("Summary")
    lines.append("=======")
    lines.append(f"Errors: {report['summary']['errors']}")
    lines.append(f"Warnings: {report['summary']['warnings']}")

    return "\n".join(lines) + "\n"
