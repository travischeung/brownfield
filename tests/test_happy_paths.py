"""Happy-path coverage. These tests encode intended product behavior only."""


def test_login_returns_bearer_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "bob@example.com",
            "password": "password123",
            "full_name": "Bob",
        },
    )
    res = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_create_and_list_tickets(client, auth_header):
    created = client.post(
        "/tickets/",
        headers=auth_header,
        json={
            "title": "Ship drill suite",
            "description": "Cover happy paths",
            "priority": "high",
        },
    )
    assert created.status_code == 201
    ticket = created.json()
    assert ticket["title"] == "Ship drill suite"
    assert ticket["status"] == "open"
    assert ticket["version"] == 1

    listed = client.get("/tickets/", headers=auth_header)
    assert listed.status_code == 200
    titles = [t["title"] for t in listed.json()]
    assert "Ship drill suite" in titles


def test_update_own_ticket(client, auth_header):
    ticket = client.post(
        "/tickets/",
        headers=auth_header,
        json={"title": "Editable", "description": "", "priority": "medium"},
    ).json()

    updated = client.patch(
        f"/tickets/{ticket['id']}",
        headers=auth_header,
        json={
            "title": "Edited title",
            "status": "in_progress",
            "expected_version": ticket["version"],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Edited title"
    assert updated.json()["status"] == "in_progress"
    assert updated.json()["version"] == ticket["version"] + 1


def test_update_version_conflict_fails_loudly(client, auth_header):
    ticket = client.post(
        "/tickets/",
        headers=auth_header,
        json={"title": "Race me", "description": "", "priority": "medium"},
    ).json()

    first = client.patch(
        f"/tickets/{ticket['id']}",
        headers=auth_header,
        json={"title": "Writer A", "expected_version": ticket["version"]},
    )
    assert first.status_code == 200
    assert first.json()["version"] == ticket["version"] + 1

    # Stale expected_version from before writer A's commit — must not succeed.
    second = client.patch(
        f"/tickets/{ticket['id']}",
        headers=auth_header,
        json={"title": "Writer B", "expected_version": ticket["version"]},
    )
    assert second.status_code == 409
    reread = client.get(f"/tickets/{ticket['id']}", headers=auth_header)
    assert reread.json()["title"] == "Writer A"


def test_patch_invalidates_ticket_cache(client, auth_header):
    created = client.post(
        "/tickets/",
        headers=auth_header,
        json={"title": "Cached", "description": "", "priority": "medium"},
    ).json()
    tid = created["id"]

    first_get = client.get(f"/tickets/{tid}", headers=auth_header)
    assert first_get.status_code == 200
    assert first_get.json()["title"] == "Cached"

    patched = client.patch(
        f"/tickets/{tid}",
        headers=auth_header,
        json={"title": "After write", "expected_version": created["version"]},
    )
    assert patched.status_code == 200

    second_get = client.get(f"/tickets/{tid}", headers=auth_header)
    assert second_get.status_code == 200
    assert second_get.json()["title"] == "After write"


def test_comment_on_own_ticket(client, auth_header):
    ticket = client.post(
        "/tickets/",
        headers=auth_header,
        json={"title": "Needs discussion", "description": "", "priority": "medium"},
    ).json()

    comment = client.post(
        f"/tickets/{ticket['id']}/comments/",
        headers=auth_header,
        json={"body": "Let's talk tomorrow"},
    )
    assert comment.status_code == 201
    assert comment.json()["body"] == "Let's talk tomorrow"
    assert comment.json()["ticket_id"] == ticket["id"]

    thread = client.get(
        f"/tickets/{ticket['id']}/comments/",
        headers=auth_header,
    )
    assert thread.status_code == 200
    assert len(thread.json()) == 1


def test_close_own_ticket(client, auth_header):
    ticket = client.post(
        "/tickets/",
        headers=auth_header,
        json={"title": "Done work", "description": "", "priority": "low"},
    ).json()

    closed = client.post(
        f"/tickets/{ticket['id']}/close",
        headers=auth_header,
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"


def test_create_with_idempotency_key_dedupes(client, auth_header):
    headers = {
        **auth_header,
        "Idempotency-Key": "retry-me-once",
    }
    body = {
        "title": "Only one please",
        "description": "",
        "priority": "medium",
    }
    first = client.post("/tickets/", headers=headers, json=body)
    second = client.post("/tickets/", headers=headers, json=body)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    listed = client.get("/tickets/", headers=auth_header)
    assert listed.status_code == 200
    matches = [t for t in listed.json() if t["title"] == "Only one please"]
    assert len(matches) == 1


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
