from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

from app.builders.b2mml_builder import build_b2mml_xml
from app.cli import model_to_json
from app.csv_export import export_classes_csv, export_equipment_csv
from app.diff import diff_models
from app.excel_export import export_to_excel
from app.html_report import export_to_html
from app.pipeline import InvalidXML, run_pipeline_from_bytes
from app.schemas import DiffResponse, HealthResponse, ModelResponse, StatsResponse
from app.stats import compute_stats

app = FastAPI(
    title="Ampla → B2MML API",
    description="Converts Ampla Project XML to ISA-95 B2MML Equipment models.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        run_pipeline_from_bytes(b"<Ampla></Ampla>")
        return {"status": "ok", "pipeline": "ready"}
    except Exception:
        return {"status": "error", "pipeline": "failed"}


@app.post("/convert/json", response_model=ModelResponse)
async def convert_json(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return model_to_json(model)


@app.post("/convert/xml", responses={200: {"content": {"application/xml": {}}}})
async def convert_xml(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    xml = build_b2mml_xml(model)
    return Response(content=xml, media_type="application/xml")


@app.post("/diff/json", response_model=DiffResponse)
async def diff_json(file_a: UploadFile, file_b: UploadFile):
    try:
        model_a = run_pipeline_from_bytes(await file_a.read())
        model_b = run_pipeline_from_bytes(await file_b.read())
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    result = diff_models(model_a, model_b)
    return result.to_dict()


@app.post("/diff/text", responses={200: {"content": {"text/plain": {}}}})
async def diff_text(file_a: UploadFile, file_b: UploadFile):
    try:
        model_a = run_pipeline_from_bytes(await file_a.read())
        model_b = run_pipeline_from_bytes(await file_b.read())
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    result = diff_models(model_a, model_b)
    return Response(content=result.to_text(), media_type="text/plain")


@app.post(
    "/convert/excel",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        }
    },
)
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


@app.post("/convert/csv/equipment", responses={200: {"content": {"text/csv": {}}}})
async def convert_csv_equipment(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return Response(
        content=export_equipment_csv(model),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=equipment.csv"},
    )


@app.post("/convert/csv/classes", responses={200: {"content": {"text/csv": {}}}})
async def convert_csv_classes(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return Response(
        content=export_classes_csv(model),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=classes.csv"},
    )


@app.post("/stats", response_model=StatsResponse)
async def stats(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return compute_stats(model).to_dict()


@app.post("/convert/html", responses={200: {"content": {"text/html": {}}}})
async def convert_html(file: UploadFile):
    xml_bytes = await file.read()
    try:
        model = run_pipeline_from_bytes(xml_bytes)
    except InvalidXML:
        raise HTTPException(status_code=400, detail="Invalid XML")
    return Response(
        content=export_to_html(model),
        media_type="text/html; charset=utf-8",
    )
