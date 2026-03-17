from fastapi import FastAPI, HTTPException, UploadFile
from lxml import etree

from app.builders.b2mml_builder import build_b2mml_xml
from app.cli import model_to_json
from app.transformers.ampla_to_b2mml import transform_ampla_to_b2mml
from app.transformers.normalize import normalize_to_xslt_semantics

app = FastAPI(title="Ampla → B2MML API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/convert/json")
async def convert_json(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        xml_bytes = await file.read()
        root = etree.fromstring(xml_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid XML")

    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    return model_to_json(model)


@app.post("/convert/xml")
async def convert_xml(file: UploadFile):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        xml_bytes = await file.read()
        root = etree.fromstring(xml_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid XML")

    model = transform_ampla_to_b2mml(root)
    normalize_to_xslt_semantics(model, root)

    xml = build_b2mml_xml(model)
    return xml
