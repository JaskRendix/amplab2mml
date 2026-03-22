from pydantic import BaseModel


class PropertySchema(BaseModel):
    name: str
    value: str | None
    datatype: str


class EquipmentSchema(BaseModel):
    id: str
    name: str | None
    level: str
    full_name: str | None
    class_ids: list[str]
    properties: list[PropertySchema]
    children: list["EquipmentSchema"] = []


EquipmentSchema.model_rebuild()


class ClassSchema(BaseModel):
    name: str
    parent: str | None
    properties: list[PropertySchema]
    inheritance_chain: list[str]


class ModelResponse(BaseModel):
    equipment: list[EquipmentSchema]
    classes: list[ClassSchema]
    warnings: list[str]


class StatsResponse(BaseModel):
    total_equipment: int
    total_classes: int
    total_properties: int
    max_depth: int
    warnings: list[str]


class PropertyChangeSchema(BaseModel):
    name: str
    old: str | None = None
    new: str | None = None
    value: str | None = None


class EquipmentPropertyChanges(BaseModel):
    equipment: str
    added: list[PropertyChangeSchema]
    removed: list[PropertyChangeSchema]
    changed: list[PropertyChangeSchema]


class ClassPropertyChanges(BaseModel):
    class_name: str
    added: list[PropertyChangeSchema]
    removed: list[PropertyChangeSchema]
    changed: list[PropertyChangeSchema]


class LevelChange(BaseModel):
    name: str
    old: str
    new: str


class DiffResponse(BaseModel):
    equipment_added: list[str]
    equipment_removed: list[str]
    equipment_level_changed: list[LevelChange]
    equipment_properties_changed: list[dict]
    classes_added: list[str]
    classes_removed: list[str]
    class_properties_changed: list[dict]


class HealthResponse(BaseModel):
    status: str
    pipeline: str
