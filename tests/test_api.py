import csv
from io import BytesIO, StringIO

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_convert_json():
    xml = open("tests/data/sample_ampla.xml").read()

    response = client.post(
        "/convert/json", files={"file": ("sample.xml", xml, "application/xml")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "equipment" in data
    assert "classes" in data


def test_convert_xml():
    xml = open("tests/data/sample_ampla.xml").read()

    response = client.post(
        "/convert/xml", files={"file": ("sample.xml", xml, "application/xml")}
    )

    assert response.status_code == 200
    assert "<ShowEquipmentInformation" in response.text


def test_invalid_xml():
    response = client.post(
        "/convert/json", files={"file": ("bad.xml", "<not-xml>", "application/xml")}
    )
    assert response.status_code in (400, 422)


def test_missing_file():
    response = client.post("/convert/json")
    assert response.status_code in (400, 422)


def test_large_file():
    xml = "<Ampla>" + (" " * 500000) + "</Ampla>"
    response = client.post(
        "/convert/json", files={"file": ("large.xml", xml, "application/xml")}
    )
    assert response.status_code == 200


def test_convert_excel():
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/excel", files={"file": ("sample.xml", xml, "application/xml")}
    )
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
    wb = load_workbook(BytesIO(response.content))
    assert "Equipment" in wb.sheetnames
    assert "Classes" in wb.sheetnames


def test_convert_excel_invalid_xml():
    response = client.post(
        "/convert/excel", files={"file": ("bad.xml", "<not-xml>", "application/xml")}
    )
    assert response.status_code in (400, 422)


def test_convert_csv_equipment():
    import csv
    from io import StringIO

    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/csv/equipment",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    rows = list(csv.DictReader(StringIO(response.text)))
    assert len(rows) > 0
    assert "full_name" in rows[0]
    assert "level" in rows[0]


def test_convert_csv_classes():
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/csv/classes",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    rows = list(csv.DictReader(StringIO(response.text)))
    assert len(rows) > 0
    assert "name" in rows[0]
    assert "parent" in rows[0]


def test_stats():
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/stats",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_equipment"] > 0
    assert data["total_classes"] > 0
    assert data["max_depth"] > 0
    assert "warnings" in data


def test_stats_invalid_xml():
    response = client.post(
        "/stats",
        files={"file": ("bad.xml", "<not-xml>", "application/xml")},
    )
    assert response.status_code in (400, 422)


def test_convert_csv_invalid_xml():
    response = client.post(
        "/convert/csv/equipment",
        files={"file": ("bad.xml", "<not-xml>", "application/xml")},
    )
    assert response.status_code in (400, 422)


def test_convert_html():
    xml = open("tests/data/sample_ampla.xml").read()
    response = client.post(
        "/convert/html",
        files={"file": ("sample.xml", xml, "application/xml")},
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "AcmeMining" in response.text


def test_convert_html_invalid_xml():
    response = client.post(
        "/convert/html",
        files={"file": ("bad.xml", "<not-xml>", "application/xml")},
    )
    assert response.status_code in (400, 422)
