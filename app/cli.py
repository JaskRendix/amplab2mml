import argparse
import json
import sys

from lxml import etree

from app.builders.b2mml_builder import build_b2mml_xml
from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml
from app.transformers.normalize import normalize_to_xslt_semantics


def run_pipeline(input_path: str):
    """Shared pipeline for both XML and JSON output."""
    with open(input_path, "rb") as f:
        root = etree.parse(f).getroot()

    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)
    return model


def model_to_json(model):
    def eq_to_dict(eq):
        return {
            "id": eq.id,
            "name": eq.name,
            "level": eq.level,
            "full_name": eq.full_name,
            "class_ids": eq.class_ids,
            "properties": [
                {
                    "name": p.name,
                    "value": p.value,
                    "datatype": p.datatype,
                }
                for p in eq.properties
            ],
            "children": [eq_to_dict(c) for c in eq.children],
        }

    def cls_to_dict(cls):
        return {
            "name": cls.name,
            "parent": cls.parent,
            "properties": [
                {
                    "name": p.name,
                    "value": p.value,
                    "datatype": p.datatype,
                }
                for p in cls.properties
            ],
            # Avoid circular references by dumping only names
            "inheritance_chain": [c.name for c in cls.inheritance_chain],
        }

    return {
        "equipment": [eq_to_dict(eq) for eq in model["equipment"]],
        "classes": [cls_to_dict(cls) for cls in model["classes"]],
    }


def main():
    parser = argparse.ArgumentParser(prog="b2mml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # convert → XML output
    convert = subparsers.add_parser("convert", help="Convert Ampla XML to B2MML XML")
    convert.add_argument("input", help="Input Ampla XML file")
    convert.add_argument("output", help="Output XML file")

    # json → JSON output
    json_cmd = subparsers.add_parser("json", help="Convert Ampla XML to JSON model")
    json_cmd.add_argument("input", help="Input Ampla XML file")
    json_cmd.add_argument("output", nargs="?", help="Optional output JSON file")

    args = parser.parse_args()

    # convert command
    if args.command == "convert":
        model = run_pipeline(args.input)
        xml = build_b2mml_xml(model)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml)
        return

    # json command
    if args.command == "json":
        model = run_pipeline(args.input)
        serializable = model_to_json(model)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        else:
            json.dump(serializable, sys.stdout, indent=2)
            sys.stdout.write("\n")
