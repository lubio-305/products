import io


def _leaf(admin_client, name="防制面"):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    return admin_client.post("/api/nodes", json={"name": name, "parent_id": top["id"]}).json()


def test_upload_pdf_with_summary(admin_client, monkeypatch):
    # 測試用的假 PDF bytes 本來就不是真的 PDF，抽不出文字層，會走到 OCR 那條路，
    # 用假的 ocr_file 避免測試環境需要真的裝 tesseract/poppler。
    monkeypatch.setattr("app.routers.attachments.ocr_file", lambda path: "")

    node = _leaf(admin_client)
    resp = admin_client.post(
        f"/api/nodes/{node['id']}/attachments",
        data={"summary": "本次公文重點：加強第三季查緝量能。"},
        files={"file": ("memo.pdf", io.BytesIO(b"%PDF-1.4 dummy"), "application/pdf")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["summary"] == "本次公文重點：加強第三季查緝量能。"


def test_scanned_image_flags_needs_ocr_without_running_real_ocr(admin_client, monkeypatch):
    """圖片上傳應該標記 needs_ocr=True，並觸發 OCR；用假的 ocr_file 避免測試環境
    需要真的安裝 tesseract 執行檔。"""
    monkeypatch.setattr("app.routers.attachments.ocr_file", lambda path: "辨識出來的文字")

    node = _leaf(admin_client)
    resp = admin_client.post(
        f"/api/nodes/{node['id']}/attachments",
        data={"summary": "掃描的公文"},
        files={"file": ("scan.png", io.BytesIO(b"\x89PNG\r\n\x1a\ndummy"), "image/png")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["needs_ocr"] is True


def test_cannot_upload_attachment_to_non_leaf_node(admin_client):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]})

    resp = admin_client.post(
        f"/api/nodes/{top['id']}/attachments",
        data={"summary": "x"},
        files={"file": ("a.pdf", io.BytesIO(b"x"), "application/pdf")},
    )
    assert resp.status_code == 400
