"""Tests for Flask web routes and API endpoints."""
from flask_app import create_app


def test_public_routes_status_code_200():
    app = create_app()
    client = app.test_client()

    for endpoint in ["/", "/dashboard", "/submit", "/assistant", "/history"]:
        res = client.get(endpoint)
        assert res.status_code == 200, f"Route {endpoint} returned {res.status_code}"


def test_language_detection_api():
    app = create_app()
    client = app.test_client()

    payload = {"code": "def process_data(items):\n    return [x * 2 for x in items]"}
    res = client.post("/api/detect-language", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["language"] == "python"


def test_chat_api_fallback_response():
    app = create_app()
    client = app.test_client()

    payload = {"question": "How can I prevent SQL injection in Python?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "answer" in data
    assert len(data.get("citations", [])) > 0


def test_submit_flow_and_exports():
    app = create_app()
    client = app.test_client()

    code_snippet = (
        "import os\n"
        "import hashlib\n"
        "def authenticate(u, p):\n"
        "    h = hashlib.md5(p.encode()).hexdigest()\n"
        "    os.system('echo user ' + u)\n"
        "    return h\n"
    )

    # 1. Post submission
    sub_res = client.post(
        "/submit",
        data={"submission_type": "paste", "code_content": code_snippet},
        follow_redirects=True,
    )
    assert sub_res.status_code == 200
    review_id = sub_res.request.path.split("/")[-1]
    assert review_id.startswith("REV-")

    # 2. Results, Findings, and Remediation views
    for path in [f"/results/{review_id}", f"/findings/{review_id}", f"/remediation/{review_id}"]:
        view_res = client.get(path)
        assert view_res.status_code == 200

    # 3. PDF Export
    pdf_res = client.get(f"/export/{review_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.data.startswith(b"%PDF")

    # 4. JSON Export
    json_res = client.get(f"/export/{review_id}/json")
    assert json_res.status_code == 200
    assert b"AI Code Review" in json_res.data
