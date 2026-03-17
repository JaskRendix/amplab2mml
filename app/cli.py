import argparse
import json
import logging
import sys

from app.builders.b2mml_builder import build_b2mml_xml
from app.pipeline import InvalidXML, run_pipeline_from_file

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def model_to_json(model):
    def eq_to_dict(eq):
        return {
            "id": eq.id,
            "name": eq.name,
            "level": eq.level,
            "full_name": eq.full_name,
            "class_ids": eq.class_ids,
            "properties": [
                {"name": p.name, "value": p.value, "datatype": p.datatype}
                for p in eq.properties
            ],
            "children": [eq_to_dict(c) for c in eq.children],
        }

    def cls_to_dict(cls):
        return {
            "name": cls.name,
            "parent": cls.parent,
            "properties": [
                {"name": p.name, "value": p.value, "datatype": p.datatype}
                for p in cls.properties
            ],
            "inheritance_chain": [c.name for c in cls.inheritance_chain],
        }

    return {
        "equipment": [eq_to_dict(eq) for eq in model["equipment"]],
        "classes": [cls_to_dict(cls) for cls in model["classes"]],
    }


def main():
    parser = argparse.ArgumentParser(prog="b2mml")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Convert Ampla XML to B2MML XML")
    convert.add_argument("input", help="Input Ampla XML file")
    convert.add_argument("output", help="Output XML file")

    json_cmd = subparsers.add_parser("json", help="Convert Ampla XML to JSON model")
    json_cmd.add_argument("input", help="Input Ampla XML file")
    json_cmd.add_argument("output", nargs="?", help="Optional output JSON file")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    try:
        logger.debug(f"Loading and transforming XML from: {args.input}")
        model = run_pipeline_from_file(args.input)
    except InvalidXML as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

    if args.command == "convert":
        logger.debug("Building B2MML XML output")
        xml = build_b2mml_xml(model)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml)
        return

    if args.command == "json":
        logger.debug("Building JSON output")
        serializable = model_to_json(model)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        else:
            json.dump(serializable, sys.stdout, indent=2)
            sys.stdout.write("\n")
