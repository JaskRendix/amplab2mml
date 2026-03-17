from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

from app.builders.b2mml_builder import build_b2mml_xml
from app.cli import model_to_json
from app.pipeline import InvalidXML, run_pipeline_from_bytes

app = FastAPI(title="Ampla → B2MML API")


@app.get("/health")
def health():
    try:
        run_pipeline_from_bytes(b"<Project></Project>")
        return {"status": "ok", "pipeline": "ready"}
    except Exception:
        return {"status": "error", "pipeline": "failed"}


@app.post("/convert/json")
async def convert_json(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return model_to_json(model)


@app.post("/convert/xml")
async def convert_xml(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")

    xml = build_b2mml_xml(model)
    return Response(content=xml, media_type="application/xml")
