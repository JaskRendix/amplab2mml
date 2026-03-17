from pydantic import BaseModel

from .properties import EquipmentProperty


class Equipment(BaseModel):
    id: str
    name: str | None = None
    level: str
    full_name: str | None = None
    properties: list[EquipmentProperty] = []
    class_ids: list[str] = []
    children: list["Equipment"] = []
    overrides: dict = {}


Equipment.model_rebuild()
