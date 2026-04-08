import logging
from pathlib import Path
from typing import Any

import tomllib

from app.models.classes import EquipmentClass
from app.models.equipment import Equipment
from app.models.properties import ClassProperty, EquipmentProperty

logger = logging.getLogger(__name__)


class TransformationContext:
    """Holds shared state for a single transformation run."""

    def __init__(self, level_map: dict[str, str]):
        self.level_map = level_map
        self.class_id_lookup: dict[str, str] = {}
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}


class AmplaTransformer:
    """Transforms Ampla XML into B2MML equipment and class models."""

    def __init__(self, config_path: str | None = "config/mapping.toml"):
        self.config_path = config_path
        self.level_map = self._load_config(config_path)

    def _load_config(self, path: str | None) -> dict[str, str]:
        """Loads level mapping from TOML or falls back to defaults."""
        default_map = {
            "Citect.Ampla.Isa95.EnterpriseFolder": "Enterprise",
            "Citect.Ampla.Isa95.SiteFolder": "Site",
            "Citect.Ampla.Isa95.AreaFolder": "Area",
            "Citect.Ampla.General.Server.ApplicationsFolder": "Other",
        }

        if not path or not Path(path).exists():
            logger.warning(f"Config path {path} not found. Using defaults.")
            return default_map

        try:
            with open(path, "rb") as f:
                config = tomllib.load(f)
                return config.get("level_map", default_map)
        except Exception as e:
            logger.error(f"Error loading config: {e}. Using defaults.")
            return default_map

    def transform(self, root: Any) -> dict[str, Any]:
        """Runs the full multi-pass transformation pipeline."""
        ctx = TransformationContext(self.level_map)

        # Pass 1: Build lookup tables
        ctx.class_id_lookup = self._build_class_id_lookup(root)

        # Pass 2: Parse class hierarchy
        classes = self._parse_classes(root)
        self._compute_class_inheritance(classes)

        # Pass 3: Parse equipment tree
        equipment = self._parse_equipment(root, ctx)

        # Pass 4: Resolve names + merge properties
        self._compute_full_names(equipment, None)
        self._merge_properties(equipment, classes)

        for cls in classes:
            cls.properties = sorted(cls.properties, key=lambda p: p.name)

        return {
            "equipment": equipment,
            "classes": classes,
            "warnings": ctx.warnings,
        }

    def _parse_classes(self, root: Any) -> list[EquipmentClass]:
        """Extracts all class definitions from the XML."""
        classes: list[EquipmentClass] = []
        for container in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
            children = container.xpath("ClassDefinition")
            nodes = children if children else [container]
            for node in nodes:
                classes.extend(self._extract_classes(node, None))
        return classes

    def _extract_classes(self, node: Any, parent: str | None) -> list[EquipmentClass]:
        """Recursively builds EquipmentClass objects."""
        name = node.get("name")
        full_name = f"{parent}.{name}" if parent else name

        props = [
            ClassProperty(
                name=p.get("name"),
                description=p.get("description"),
                value=p.text,
                datatype=self._translate_datatype(p.get("type")),
            )
            for p in node.xpath("PropertyDefinition")
        ]

        cls = EquipmentClass(name=full_name, parent=parent, properties=props)
        result = [cls]

        for child in node.xpath("ClassDefinition"):
            result.extend(self._extract_classes(child, full_name))

        return result

    def _build_class_id_lookup(self, root: Any) -> dict[str, str]:
        """Maps ClassDefinition @id → dotted class name."""
        lookup: dict[str, str] = {}

        def walk(node: Any, parent: str | None):
            name = node.get("name")
            full = f"{parent}.{name}" if parent else name
            if node_id := node.get("id"):
                lookup[node_id] = full
            for child in node.xpath("ClassDefinition"):
                walk(child, full)

        for container in root.xpath("/Ampla/ClassDefinitions/ClassDefinition"):
            children = container.xpath("ClassDefinition")
            nodes = children if children else [container]
            for node in nodes:
                walk(node, None)

        return lookup

    def _compute_class_inheritance(self, classes: list[EquipmentClass]):
        """Builds inheritance chains for all classes."""
        lookup = {cls.name: cls for cls in classes}
        for cls in classes:
            chain = []
            current = cls
            while current:
                chain.append(current)
                current = lookup.get(current.parent)
            cls.inheritance_chain = chain[::-1]

    def _parse_equipment(
        self, root: Any, ctx: TransformationContext
    ) -> list[Equipment]:
        """Extracts all equipment items and resolves their class IDs."""
        return [
            eq
            for item in root.xpath("/Ampla/Item")
            if (eq := self._convert_item(item, ctx))
        ]

    def _convert_item(self, node: Any, ctx: TransformationContext) -> Equipment | None:
        """Converts an <Item> XML node into an Equipment model."""
        try:
            item_type = node.get("type", "Unknown")
            level = self.level_map.get(item_type, "Other")

            raw_ids = [
                a.get("classDefinitionId") for a in node.xpath("ItemClassAssociation")
            ]
            resolved_class_names = [self._resolve_class_id(cid, ctx) for cid in raw_ids]

            return Equipment(
                id=node.get("id"),
                name=node.get("name", ""),
                level=level,
                children=[
                    c for n in node.xpath("Item") if (c := self._convert_item(n, ctx))
                ],
                properties=[],
                class_ids=resolved_class_names,
                overrides={p.get("name"): p.text for p in node.xpath("Property")},
            )
        except Exception as e:
            logger.error(f"Faulty item detected at ID {node.get('id')}: {e}")
            return None

    def _resolve_class_id(self, cid: Any, ctx: TransformationContext):
        name = ctx.class_id_lookup.get(cid)
        if not name:
            ctx.warnings.append(f"Unknown class ID '{cid}'")
        return name or cid

    def _compute_full_names(self, equipment_list: list[Equipment], parent: str | None):
        """Computes dotted full names for all equipment nodes."""
        for eq in equipment_list:
            eq.full_name = (
                f"{parent}.{eq.name}"
                if parent and eq.name
                else (eq.name or parent or "")
            )
            self._compute_full_names(eq.children, eq.full_name)

    def _merge_properties(
        self, equipment: list[Equipment], classes: list[EquipmentClass]
    ):
        """Merges inherited class properties with equipment overrides."""
        class_lookup = {cls.name: cls for cls in classes}

        def process(eq: Equipment):
            merged: dict[str, EquipmentProperty] = {}

            # 1. Inherit from classes
            for class_name in eq.class_ids:
                cls = class_lookup.get(class_name)
                if not cls:
                    continue
                for ancestor in cls.inheritance_chain:
                    for p in ancestor.properties:
                        merged[p.name] = EquipmentProperty(
                            name=p.name, value=p.value, datatype=p.datatype
                        )

            # 2. Apply instance overrides
            for key, val in eq.overrides.items():
                prop_name = key.split(".", 1)[1] if key.startswith("Class.") else key
                if prop_name in merged:
                    merged[prop_name].value = val
                else:
                    merged[prop_name] = EquipmentProperty(
                        name=prop_name, value=val, datatype="string"
                    )

            eq.properties = sorted(merged.values(), key=lambda p: p.name)

            for child in eq.children:
                process(child)

        for e in equipment:
            process(e)

    def _translate_datatype(self, dt: str | None) -> str:
        """Translates Ampla datatypes to B2MML datatypes."""
        mapping = {"System.String": "string", "System.Int32": "int"}
        return mapping.get(dt or "", "string")
