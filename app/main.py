from fastapi import FastAPI, UploadFile

from app.builders.b2mml_builder import build_b2mml_xml
from app.parsers.ampla_parser import parse_ampla_xml
from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml

app = FastAPI()


@app.post("/transform/ampla-to-b2mml")
async def transform(file: UploadFile):
    xml_bytes = await file.read()
    ampla_tree = parse_ampla_xml(xml_bytes)
    model = transform_ampla_to_b2mml(ampla_tree)
    output_xml = build_b2mml_xml(model)
    return {"b2mml": output_xml}
