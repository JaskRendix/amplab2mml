# Ampla to B2MML Transformer

This project converts an Ampla Project XML export into an ISA-95 B2MML Equipment model.
It replaces the original XSLT-only approach with a Python implementation that provides
a command-line interface, a FastAPI service, and multiple output formats.

---

## Purpose

Ampla Project XML files contain equipment definitions, hierarchy, classes, and properties.
This tool reads that XML and produces:

- B2MML Equipment XML
- JSON model
- Excel workbook (.xlsx) with Equipment and Classes sheets
- CSV files for equipment and classes

It also provides:

- Validation warnings for structural issues in the source data
- Diff mode to compare two Ampla configurations and report what changed
- Stats summary with equipment counts, class counts, property totals, and hierarchy depth

The transformer is fully tested and suitable for automation, integration, and
comparison of Ampla project configurations.

---

## Origin

This project is a direct Python reimplementation of the original XSLT stylesheet
published at https://github.com/Ampla/Project-To-B2MML.
It reproduces the transformation logic faithfully and adds a CLI, REST API,
multiple output formats, and a full test suite including a regression fixture
verified against the original XSLT behaviour.

---

## Installation

### 1. Clone the repository
```
git clone https://github.com/<your-username>/amplab2mml.git
cd amplab2mml
```

### 2. Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

---

## Command-line usage

### Convert Ampla XML to B2MML XML
```
b2mml convert input.xml output.xml
```

### Convert to JSON
```
b2mml json input.xml output.json
```
If no output file is provided, JSON is written to stdout:
```
b2mml json input.xml
```

### Export to Excel
```
b2mml excel input.xml output.xlsx
```

### Show model statistics
```
b2mml stats input.xml
```
Output as JSON:
```
b2mml stats --format json input.xml
```

### Export to HTML report
```
b2mml html input.xml report.html
```

### Diff two Ampla XML files
```
b2mml diff baseline.xml updated.xml
```
Output as JSON:
```
b2mml diff --format json baseline.xml updated.xml
```
Save to file:
```
b2mml diff baseline.xml updated.xml diff.txt
```
Exits with code `0` if no differences, `1` if differences found — suitable for CI.

---

## API usage

Start the FastAPI server:
```
uvicorn app.api:app --reload
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/info` | API and pipeline version info |
| POST | `/convert/json` | Receive JSON model |
| POST | `/convert/xml` | Receive B2MML XML |
| POST | `/convert/excel` | Receive Excel workbook |
| POST | `/convert/csv/equipment` | Receive equipment CSV |
| POST | `/convert/csv/classes` | Receive classes CSV |
| POST | `/convert/html` | Receive HTML report |
| POST | `/stats` | Receive model statistics |
| POST | `/diff/json` | Diff two files, receive JSON |
| POST | `/diff/text` | Diff two files, receive plain text |

All `/convert/*` and `/stats` endpoints accept a single `file` upload field.
`/diff/*` endpoints accept `file_a` and `file_b`.
Interactive API docs are available at `http://localhost:8000/docs` once the server is running.

Examples:
```
curl -X POST -F "file=@input.xml" http://localhost:8000/convert/json
curl -X POST -F "file=@input.xml" http://localhost:8000/stats
curl -X POST -F "file_a=@baseline.xml" -F "file_b=@updated.xml" http://localhost:8000/diff/text
```

---

## Docker Compose (local development)

The project includes a Docker Compose setup for running the API with hot-reload and without needing to rebuild the image on every change.

### Start the API
```
make up
```

The service will be available at:

```
http://localhost:8000
```

### Stop the service
```
make down
```

---

## Project structure

- `app/parsers` — parses Ampla Project XML into an lxml element tree
- `app/transformers` — converts the parsed tree into an internal equipment and class model
- `app/builders` — serialises the model to B2MML XML
- `app/validators.py` — validates the model and returns human-readable warnings
- `app/diff.py` — compares two models and reports structural differences
- `app/stats.py` — computes summary statistics from the model
- `app/excel_export.py` — exports the model to an Excel workbook
- `app/csv_export.py` — exports the model to CSV
- `app/cli.py` — command-line interface
- `app/api.py` — FastAPI application
- `app/html_report.py` — exports the model to a self-contained HTML report
- `app/schemas.py` — Pydantic response models for the FastAPI endpoints
- `tests/` — full test suite including regression fixtures verified against the original XSLT

---

## License

This project is licensed under the BSD 3-Clause License.
It includes third-party material derived from the original
`Ampla_to_Equipment_B2MML.xslt` by Oleg Tkachenko (2005),
also under the BSD 3-Clause License.
