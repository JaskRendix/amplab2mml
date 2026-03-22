from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

from app.builders.b2mml_builder import build_b2mml_xml
from app.cli import model_to_json
from app.diff import diff_models
from app.excel_export import export_to_excel
from app.pipeline import InvalidXML, run_pipeline_from_bytes

app = FastAPI(title="Ampla → B2MML API")


@app.get("/health")
def health():
    try:
        run_pipeline_from_bytes(b"<Ampla></Ampla>")
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


@app.post("/diff/json")
async def diff_json(file_a: UploadFile, file_b: UploadFile):
    try:
        model_a = run_pipeline_from_bytes(await file_a.read())
        model_b = run_pipeline_from_bytes(await file_b.read())
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    result = diff_models(model_a, model_b)
    return result.to_dict()


@app.post("/diff/text")
async def diff_text(file_a: UploadFile, file_b: UploadFile):
    try:
        model_a = run_pipeline_from_bytes(await file_a.read())
        model_b = run_pipeline_from_bytes(await file_b.read())
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    result = diff_models(model_a, model_b)
    return Response(content=result.to_text(), media_type="text/plain")


@app.post("/convert/excel")
async def convert_excel(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    data = export_to_excel(model)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=equipment.xlsx"},
    )
