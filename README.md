# Ampla to B2MML Transformer

This project converts an Ampla Project XML export into an ISA‑95 B2MML Equipment model. It replaces the original XSLT‑only approach with a Python implementation that provides a command‑line interface, a FastAPI service, and JSON output.

---

## Purpose

Ampla Project XML files contain equipment definitions, hierarchy, classes, and properties. This tool reads that XML, normalizes it to match the behavior of the original XSLT, and produces either:

- B2MML Equipment XML  
- a structured JSON model  

The transformer is fully tested and suitable for automation, integration, and comparison of Ampla project configurations.

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

---

## API usage

Start the FastAPI server:

```
uvicorn app.main:app --reload
```

### Endpoints

- `GET /health` — basic health check  
- `POST /convert/json` — upload an Ampla XML file, receive JSON  
- `POST /convert/xml` — upload an Ampla XML file, receive B2MML XML  

Example using `curl`:

```
curl -X POST -F "file=@tests/data/sample_ampla.xml" http://localhost:8000/convert/json
```

---

## Project structure

- `app/parsers` — reads Ampla XML  
- `app/transformers` — converts to internal model and applies normalization  
- `app/builders` — generates B2MML XML  
- `app/cli.py` — command‑line interface  
- `app/api.py` — FastAPI application  
- `tests/` — full test suite  

---

## License

This project is licensed under the BSD 3‑Clause License.  
It includes third‑party material derived from the original `Ampla_to_Equipment_B2MML.xslt` by Oleg Tkachenko (2005), also under the BSD 3‑Clause License.
