from pydantic import BaseModel

from .properties import ClassProperty


class EquipmentClass(BaseModel):
    name: str
    parent: str | None = None
    properties: list[ClassProperty]
    inheritance_chain: list["EquipmentClass"] = []
