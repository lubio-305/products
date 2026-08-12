import io
from urllib.parse import unquote


def _leaf(admin_client, name="防制面"):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    return admin_client.post("/api/nodes", json={"name": name, "parent_id": top["id"]}).json()


def test_first_upload_is_version_1(admin_client):
    node = _leaf(admin_client)
    resp = admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "詐欺防制規定", "effective_date": "2025-01-01"},
        files={"file": ("rule.pdf", io.BytesIO(b"dummy pdf content"), "application/pdf")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["version_no"] == 1
    assert body["expired_date"] is None


def test_second_upload_expires_previous_version(admin_client):
    node = _leaf(admin_client)
    admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "舊版規定", "effective_date": "2025-01-01"},
        files={"file": ("v1.pdf", io.BytesIO(b"v1"), "application/pdf")},
    )
    admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "新版規定", "effective_date": "2025-06-01"},
        files={"file": ("v2.pdf", io.BytesIO(b"v2"), "application/pdf")},
    )

    versions = admin_client.get(f"/api/nodes/{node['id']}/regulations").json()
    assert len(versions) == 2
    by_version = {v["version_no"]: v for v in versions}
    assert by_version[1]["expired_date"] == "2025-06-01"
    assert by_version[2]["expired_date"] is None


def test_cannot_upload_regulation_to_non_leaf_node(admin_client):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]})

    resp = admin_client.post(
        f"/api/nodes/{top['id']}/regulations",
        data={"title": "規定", "effective_date": "2025-01-01"},
        files={"file": ("v1.pdf", io.BytesIO(b"v1"), "application/pdf")},
    )
    assert resp.status_code == 400


def test_can_download_uploaded_regulation(admin_client):
    node = _leaf(admin_client)
    uploaded = admin_client.post(
        f"/api/nodes/{node['id']}/regulations",
        data={"title": "詐欺防制規定", "effective_date": "2025-01-01"},
        files={"file": ("rule.pdf", io.BytesIO(b"real file content"), "application/pdf")},
    ).json()

    resp = admin_client.get(f"/api/nodes/{node['id']}/regulations/{uploaded['id']}/download")
    assert resp.status_code == 200
    assert resp.content == b"real file content"
    # 中文檔名會被瀏覽器/伺服器依 RFC 6266 編碼成 filename*=utf-8''...，解碼回來比對
    assert "詐欺防制規定_v1.pdf" in unquote(resp.headers["content-disposition"])


def test_download_regulation_wrong_node_is_404(admin_client):
    node_a = _leaf(admin_client, name="防制面")
    node_b = _leaf(admin_client, name="查緝面")
    uploaded = admin_client.post(
        f"/api/nodes/{node_a['id']}/regulations",
        data={"title": "規定", "effective_date": "2025-01-01"},
        files={"file": ("v1.pdf", io.BytesIO(b"v1"), "application/pdf")},
    ).json()

    resp = admin_client.get(f"/api/nodes/{node_b['id']}/regulations/{uploaded['id']}/download")
    assert resp.status_code == 404


def test_download_missing_regulation_is_404(admin_client):
    node = _leaf(admin_client)
    resp = admin_client.get(f"/api/nodes/{node['id']}/regulations/9999/download")
    assert resp.status_code == 404
