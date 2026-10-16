def test_short_title_returns_422(client):
    response = client.post(
        "/api/v1/issues/",
        json={
            "title": "Hi",
            "description": "Login fails with valid credentials",
        },
    )

    assert response.status_code == 422


def test_create_issue(client):
    payload = {
        "title": "Fix login error",
        "description": "Login fails with valid credentials",
    }

    response = client.post("/api/v1/issues/", json=payload)

    assert response.status_code == 201

    body = response.json()
    assert body["id"]
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["priority"] == "medium"
    assert body["status"] == "open"


def test_get_issue(client):
    payload = {
        "title": "Fix login error",
        "description": "Login fails with valid credentials",
    }

    created_response = client.post("/api/v1/issues/", json=payload)
    assert created_response.status_code == 201

    created_issue = created_response.json()
    issue_id = created_issue["id"]

    response = client.get(f"/api/v1/issues/{issue_id}")

    assert response.status_code == 200
    assert response.json() == created_issue


def test_get_unknown_issue(client):
    expected_body = {"detail": "Issue not found"}
    response = client.get(f"/api/v1/issues/unknown-id")

    assert response.status_code == 404
    assert response.json() == expected_body


def test_update_issue(client):
    payload = {
        "title": "Fix login error",
        "description": "Login fails with valid credentials",
    }

    created = client.post("/api/v1/issues/", json=payload)
    assert created.status_code == 201
    issue_id = created.json()["id"]

    response = client.put(
        f"/api/v1/issues/{issue_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    # Fetch again to check that the change was saved.
    fetched = client.get(f"/api/v1/issues/{issue_id}")

    assert fetched.status_code == 200
    assert fetched.json()["status"] == "in_progress"
    assert fetched.json()["title"] == payload["title"]


def test_delete_issue(client):
    payload = {
        "title": "Fix login error",
        "description": "Login fails with valid credentials",
    }

    created = client.post("/api/v1/issues/", json=payload)
    assert created.status_code == 201
    issue_id = created.json()["id"]

    url = f"/api/v1/issues/{issue_id}"

    response = client.delete(url)

    assert response.status_code == 204
    assert response.content == b""

    fetched = client.get(url)

    assert fetched.status_code == 404
    assert fetched.json() == {"detail": "Issue not found"}
