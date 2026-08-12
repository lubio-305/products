import io


def _leaf(admin_client, name="防制面"):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    return admin_client.post("/api/nodes", json={"name": name, "parent_id": top["id"]}).json()


def test_my_uploads_is_empty_by_default(admin_client):
    resp = admin_client.get("/api/my/uploads")
    assert resp.status_code == 200
    assert resp.json() == []


def test_my_uploads_lists_own_regulation_and_attachment(admin_client, monkeypatch):
    monkeypatch.setattr("app.routers.attachments.ocr_file", lambda path: "")

    node = _leaf(admin_client)
    admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "詐欺防制規定", "effective_date": "2025-01-01"},
        files={"file": ("rule.pdf", io.BytesIO(b"v1"), "application/pdf")},
    )
    admin_client.post(
        f"/api/nodes/{node['id']}/attachments",
        data={"summary": "重點"},
        files={"file": ("memo.pdf", io.BytesIO(b"memo"), "application/pdf")},
    )

    uploads = admin_client.get("/api/my/uploads").json()
    assert len(uploads) == 2
    types = {u["type"] for u in uploads}
    assert types == {"regulation", "attachment"}
    for u in uploads:
        assert u["node_id"] == node["id"]
        assert u["node_name"] == "防制面"


def test_my_uploads_does_not_include_other_users_files(admin_client, staff_client, staff_user):
    node = _leaf(admin_client)
    admin_client.post(
        f"/api/nodes/{node['id']}/assignments",
        json={"user_id": staff_user.id, "role": "primary"},
    )
    admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "管理者上傳的規定", "effective_date": "2025-01-01"},
        files={"file": ("rule.pdf", io.BytesIO(b"v1"), "application/pdf")},
    )

    resp = staff_client.get("/api/my/uploads")
    assert resp.status_code == 200
    assert resp.json() == []
