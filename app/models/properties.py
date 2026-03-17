from pydantic import BaseModel


class EquipmentProperty(BaseModel):
    name: str
    value: str | None
    datatype: str


class ClassProperty(BaseModel):
    name: str
    description: str | None
    value: str | None
    datatype: str
