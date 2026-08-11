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
        json={"title": "Edited title", "status": "in_progress"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Edited title"
    assert updated.json()["status"] == "in_progress"


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


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
