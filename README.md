# Ampla to B2MML Transformer

This project converts an Ampla Project XML export into an ISA‑95 B2MML Equipment model. It replaces the original XSLT‑only approach with a Python implementation that provides a command‑line interface, a FastAPI service, and JSON output.

---

## Purpose

Ampla Project XML files contain equipment definitions, hierarchy, classes, and properties.
This tool reads that XML and produces either:
- B2MML Equipment XML
- a structured JSON model

It also provides validation warnings for structural issues in the source data,
and a diff mode to compare two Ampla configurations and report what changed.

The transformer is fully tested and suitable for automation, integration, and
comparison of Ampla project configurations.

---

## Origin

This project is a direct Python reimplementation of the original XSLT
stylesheet published at https://github.com/Ampla/Project-To-B2MML.
It reproduces the transformation logic faithfully and adds a CLI, REST
API, JSON output, and a full test suite including a regression fixture
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

## Command‑line usage

### Convert Ampla XML to B2MML XML

```
b2mml convert tests/data/sample_ampla.xml output.xml
```

### Convert Ampla XML to JSON

```
b2mml json tests/data/sample_ampla.xml output.json
```

If no output file is provided, JSON is written to stdout:

```
b2mml json tests/data/sample_ampla.xml
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

- `GET /health` — basic health check
- `POST /convert/json` — upload an Ampla XML file, receive JSON
- `POST /convert/xml` — upload an Ampla XML file, receive B2MML XML
- `POST /diff/json` — upload two Ampla XML files, receive a JSON diff
- `POST /diff/text` — upload two Ampla XML files, receive a plain text diff

Example:
```
curl -X POST -F "file=@tests/data/sample_ampla.xml" http://localhost:8000/convert/json
curl -X POST -F "file_a=@baseline.xml" -F "file_b=@updated.xml" http://localhost:8000/diff/text
```

---

## Project structure

- `app/parsers` — parses Ampla Project XML into an lxml element tree
- `app/transformers` — converts the parsed tree into an internal equipment and class model
- `app/builders` — serialises the model to B2MML XML
- `app/validators.py` — validates the model and returns human-readable warnings
- `app/diff.py` — compares two models and reports structural differences
- `app/cli.py` — command-line interface
- `app/api.py` — FastAPI application
- `tests/` — full test suite including regression fixtures verified against the original XSLT

---

## License

This project is licensed under the BSD 3‑Clause License.  
It includes third‑party material derived from the original `Ampla_to_Equipment_B2MML.xslt` by Oleg Tkachenko (2005), also under the BSD 3‑Clause License.
