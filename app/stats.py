from dataclasses import dataclass, field


@dataclass
class ModelStats:
    total_equipment: int = 0
    total_classes: int = 0
    total_properties: int = 0
    max_depth: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_equipment": self.total_equipment,
            "total_classes": self.total_classes,
            "total_properties": self.total_properties,
            "max_depth": self.max_depth,
            "warnings": self.warnings,
        }

    def to_text(self) -> str:
        lines = [
            f"Equipment nodes : {self.total_equipment}",
            f"Classes         : {self.total_classes}",
            f"Properties      : {self.total_properties}",
            f"Max depth       : {self.max_depth}",
        ]
        if self.warnings:
            lines.append(f"Warnings        : {len(self.warnings)}")
            for w in self.warnings:
                lines.append(f"  ! {w}")
        else:
            lines.append("Warnings        : 0")
        return "\n".join(lines)


def compute_stats(model: dict) -> ModelStats:
    stats = ModelStats()
    stats.warnings = model.get("warnings", [])
    stats.total_classes = len(model["classes"])

    for eq in model["equipment"]:
        _walk(eq, depth=1, stats=stats)

    return stats


def _walk(eq, depth: int, stats: ModelStats):
    stats.total_equipment += 1
    stats.total_properties += len(eq.properties)
    if depth > stats.max_depth:
        stats.max_depth = depth
    for child in eq.children:
        _walk(child, depth + 1, stats)
