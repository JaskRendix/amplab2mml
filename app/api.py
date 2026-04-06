from importlib.metadata import version

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response

from app.builders.b2mml_builder import build_b2mml_xml
from app.cli import model_to_json
from app.csv_export import export_classes_csv, export_equipment_csv
from app.diff import diff_models
from app.excel_export import export_to_excel
from app.html_report import export_to_html
from app.logging_setup import (
    log_invalid_xml,
    logger,
    request_id_middleware,
    request_logging_middleware,
)
from app.pipeline import InvalidXML, run_pipeline_from_bytes
from app.schemas import DiffResponse, HealthResponse, ModelResponse, StatsResponse
from app.stats import compute_stats

PIPELINE_VERSION = version("amplab2mml")


app = FastAPI(
    title="Ampla → B2MML API",
    description="Converts Ampla Project XML to ISA-95 B2MML Equipment models.",
    version="1.0.0",
)

app.middleware("http")(request_id_middleware)
app.middleware("http")(request_logging_middleware)


async def load_model(file: UploadFile, request: Request, endpoint: str):
    if file is None:
        raise HTTPException(status_code=400, detail="Missing file upload")

    try:
        return run_pipeline_from_bytes(await file.read())
    except InvalidXML:
        log_invalid_xml(endpoint, request)
        raise HTTPException(status_code=400, detail="Invalid XML")


def binary_response(data: bytes, filename: str, media_type: str):
    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["system"],
    summary="Health check",
    operation_id="health",
)
def health():
    try:
        run_pipeline_from_bytes(b"<Ampla></Ampla>")
        return {"status": "ok", "pipeline": "ready"}
    except Exception:
        logger.error("Health check failed")
        return {"status": "error", "pipeline": "failed"}


@app.get(
    "/info",
    tags=["system"],
    summary="API and pipeline version info",
    operation_id="info",
)
def info():
    return {
        "api_version": app.version,
        "pipeline_version": PIPELINE_VERSION,
        "commit": "unknown",
    }


@app.post(
    "/convert/json",
    response_model=ModelResponse,
    tags=["convert"],
    summary="Convert Ampla XML to JSON model",
    operation_id="convert_json",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {"type": "object"},
                    "example": {
                        "file": {
                            "filename": "project.xml",
                            "content": "<Ampla>...</Ampla>",
                        }
                    },
                }
            }
        }
    },
)
async def convert_json(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/json")
    return model_to_json(model)


@app.post(
    "/convert/xml",
    tags=["convert"],
    summary="Convert Ampla XML to B2MML XML",
    operation_id="convert_xml",
    responses={200: {"content": {"application/xml": {}}}},
)
async def convert_xml(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/xml")
    xml = build_b2mml_xml(model)
    return Response(content=xml, media_type="application/xml")


@app.post(
    "/diff/json",
    response_model=DiffResponse,
    tags=["diff"],
    summary="Compute JSON diff between two Ampla XML models",
    operation_id="diff_json",
)
async def diff_json(file_a: UploadFile, file_b: UploadFile, request: Request):
    model_a = await load_model(file_a, request, "/diff/json")
    model_b = await load_model(file_b, request, "/diff/json")

    result = diff_models(model_a, model_b)
    return result.to_dict()


@app.post(
    "/diff/text",
    tags=["diff"],
    summary="Compute text diff between two Ampla XML models",
    operation_id="diff_text",
    responses={200: {"content": {"text/plain": {}}}},
)
async def diff_text(file_a: UploadFile, file_b: UploadFile, request: Request):
    model_a = await load_model(file_a, request, "/diff/text")
    model_b = await load_model(file_b, request, "/diff/text")

    result = diff_models(model_a, model_b)
    return Response(content=result.to_text(), media_type="text/plain")


@app.post(
    "/convert/excel",
    tags=["convert"],
    summary="Convert Ampla XML to Excel workbook",
    operation_id="convert_excel",
)
async def convert_excel(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/excel")
    data = export_to_excel(model)
    return binary_response(
        data,
        filename="equipment.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.post(
    "/convert/csv/equipment",
    tags=["convert"],
    summary="Export equipment list as CSV",
    operation_id="convert_csv_equipment",
)
async def convert_csv_equipment(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/csv/equipment")
    data = export_equipment_csv(model)
    return binary_response(data, "equipment.csv", "text/csv")


@app.post(
    "/convert/csv/classes",
    tags=["convert"],
    summary="Export class list as CSV",
    operation_id="convert_csv_classes",
)
async def convert_csv_classes(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/csv/classes")
    data = export_classes_csv(model)
    return binary_response(data, "classes.csv", "text/csv")


@app.post(
    "/stats",
    response_model=StatsResponse,
    tags=["stats"],
    summary="Compute statistics for an Ampla XML model",
    operation_id="stats",
)
async def stats(file: UploadFile, request: Request):
    model = await load_model(file, request, "/stats")
    return compute_stats(model).to_dict()


@app.post(
    "/convert/html",
    tags=["convert"],
    summary="Generate HTML equipment report",
    operation_id="convert_html",
)
async def convert_html(file: UploadFile, request: Request):
    model = await load_model(file, request, "/convert/html")
    html = export_to_html(model)
    return Response(content=html, media_type="text/html; charset=utf-8")
