# **Ampla to B2MML Transformer**

This project converts an **Ampla Project XML export** into an **ISA‑95 B2MML Equipment model**.  
It replaces the original XSLT‑only approach with a modern Python implementation featuring:

- a command‑line interface  
- a FastAPI service  
- multiple output formats  
- a fully tested, deterministic multi‑pass transformation pipeline  

---

## **Purpose**

Ampla Project XML files contain:

- equipment hierarchy  
- equipment classes  
- class inheritance  
- class and instance properties  

This tool parses the XML and produces:

- **B2MML Equipment XML**
- **JSON model**
- **Excel workbook (.xlsx)** with Equipment and Classes sheets
- **CSV exports**
- **HTML report**

Additional capabilities:

- **Validation warnings** for structural issues (unknown class IDs, malformed items, missing config)
- **Diff mode** to compare two Ampla configurations
- **Statistics summary** (equipment counts, class counts, property totals, hierarchy depth)

The transformer is deterministic, regression‑tested, and suitable for automation, CI, and configuration comparison.

---

## **Architecture**

The transformation pipeline is implemented in a multi‑pass class:

```python
from app.transformers.ampla import AmplaTransformer
```

The pipeline performs:

1. **Class ID lookup construction**  
2. **Class hierarchy extraction**  
3. **Inheritance chain computation**  
4. **Equipment tree parsing**  
5. **Full‑name resolution**  
6. **Property merging** (class inheritance + instance overrides)  
7. **Sorting and normalization**

This reproduces the behaviour of the original XSLT while adding validation, configurability, and structured warnings.

---

## **Configuration (mapping.toml)**

Level mapping is now externalized in:

```
config/mapping.toml
```

Example:

```toml
[level_map]
"Citect.Ampla.Isa95.EnterpriseFolder" = "Enterprise"
"Citect.Ampla.Isa95.SiteFolder" = "Site"
"Citect.Ampla.Isa95.AreaFolder" = "Area"
"Citect.Ampla.General.Server.ApplicationsFolder" = "Other"
```

If the file is missing or invalid, the transformer logs a warning and falls back to defaults.

---

## **Programmatic usage**

```python
from lxml import etree
from app.transformers.ampla import AmplaTransformer

# Parse XML
root = etree.parse("input.xml").getroot()

# Create transformer (loads mapping.toml automatically)
transformer = AmplaTransformer(config_path="config/mapping.toml")

# Run transformation
model = transformer.transform(root)

print(model["equipment"])
print(model["classes"])
print(model["warnings"])   # non-fatal issues detected during parsing
```

The returned model is a dictionary:

```python
{
    "equipment": [...],
    "classes": [...],
    "warnings": [...]
}
```

---

## **Command-line usage**

### Convert Ampla XML to B2MML XML
```
b2mml convert input.xml output.xml
```

### Convert to JSON
```
b2mml json input.xml output.json
```

Write to stdout:
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

As JSON:
```
b2mml stats --format json input.xml
```

### Export HTML report
```
b2mml html input.xml report.html
```

### Diff two Ampla XML files
```
b2mml diff baseline.xml updated.xml
```

As JSON:
```
b2mml diff --format json baseline.xml updated.xml
```

Exit codes:
- `0` → no differences  
- `1` → differences found  

---

## **API usage**

Start the FastAPI server:

```
uvicorn app.api:app --reload
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/info` | API and pipeline version info |
| POST | `/convert/json` | JSON model |
| POST | `/convert/xml` | B2MML XML |
| POST | `/convert/excel` | Excel workbook |
| POST | `/convert/csv/equipment` | Equipment CSV |
| POST | `/convert/csv/classes` | Classes CSV |
| POST | `/convert/html` | HTML report |
| POST | `/stats` | Model statistics |
| POST | `/diff/json` | JSON diff |
| POST | `/diff/text` | Text diff |

Examples:

```
curl -X POST -F "file=@input.xml" http://localhost:8000/convert/json
curl -X POST -F "file=@input.xml" http://localhost:8000/stats
curl -X POST -F "file_a=@baseline.xml" -F "file_b=@updated.xml" http://localhost:8000/diff/text
```

Interactive docs:  
`http://localhost:8000/docs`

---

## **Docker Compose (local development)**

Start the API:

```
make up
```

Service available at:

```
http://localhost:8000
```

Stop:

```
make down
```

---

## **Project structure**

- `app/parsers` — XML parsing  
- `app/transformers` — Ampla → internal model  
- `app/builders` — B2MML XML serialization  
- `app/validators.py` — model validation + warnings  
- `app/diff.py` — structural diff engine  
- `app/stats.py` — statistics computation  
- `app/excel_export.py` — Excel export  
- `app/csv_export.py` — CSV export  
- `app/html_report.py` — HTML report generator  
- `app/cli.py` — CLI entrypoints  
- `app/api.py` — FastAPI service  
- `app/schemas.py` — Pydantic response models  
- `tests/` — full test suite + regression fixtures  

---

## **License**

BSD 3‑Clause License.  
Includes derivative work from the original  
`Ampla_to_Equipment_B2MML.xslt` by Oleg Tkachenko (2005),  
also under BSD 3‑Clause.
