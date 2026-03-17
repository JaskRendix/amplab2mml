from fastapi.testclient import TestClient

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
