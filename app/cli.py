import argparse
import json
import logging
import sys

from app.builders.b2mml_builder import build_b2mml_xml
from app.diff import diff_models
from app.excel_export import export_to_excel
from app.html_report import export_to_html
from app.pipeline import InvalidXML, run_pipeline_from_file
from app.stats import compute_stats

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
        "warnings": model.get("warnings", []),
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

    excel_cmd = subparsers.add_parser("excel", help="Export Ampla XML to Excel")
    excel_cmd.add_argument("input", help="Input Ampla XML file")
    excel_cmd.add_argument("output", help="Output .xlsx file")

    html_cmd = subparsers.add_parser("html", help="Export Ampla XML to HTML report")
    html_cmd.add_argument("input", help="Input Ampla XML file")
    html_cmd.add_argument("output", help="Output .html file")

    stats_cmd = subparsers.add_parser("stats", help="Show model statistics")
    stats_cmd.add_argument("input", help="Input Ampla XML file")
    stats_cmd.add_argument("--format", choices=["text", "json"], default="text")

    diff_cmd = subparsers.add_parser("diff", help="Diff two Ampla XML files")
    diff_cmd.add_argument("input_a", help="First Ampla XML file (baseline)")
    diff_cmd.add_argument("input_b", help="Second Ampla XML file (changed)")
    diff_cmd.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    diff_cmd.add_argument("output", nargs="?", help="Optional output file")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.command == "diff":
        try:
            model_a = run_pipeline_from_file(args.input_a)
            model_b = run_pipeline_from_file(args.input_b)
        except InvalidXML as e:
            logger.error(str(e))
            sys.exit(1)

        result = diff_models(model_a, model_b)

        if args.format == "json":
            output = json.dumps(result.to_dict(), indent=2)
        else:
            output = result.to_text()

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
        else:
            print(output)

        sys.exit(0 if result.is_empty() else 1)

    try:
        model = run_pipeline_from_file(args.input)
    except InvalidXML as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

    if args.command == "convert":
        xml = build_b2mml_xml(model)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml)

    elif args.command == "json":
        serializable = model_to_json(model)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        else:
            json.dump(serializable, sys.stdout, indent=2)
            sys.stdout.write("\n")

    elif args.command == "excel":
        data = export_to_excel(model)
        with open(args.output, "wb") as f:
            f.write(data)

    elif args.command == "stats":
        stats = compute_stats(model)
        if args.format == "json":
            print(json.dumps(stats.to_dict(), indent=2))
        else:
            print(stats.to_text())

    elif args.command == "html":
        html = export_to_html(model)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
