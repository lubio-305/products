def test_admin_can_create_top_level_node(admin_client):
    resp = admin_client.post("/api/nodes", json={"name": "詐欺業務"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "詐欺業務"
    assert body["parent_id"] is None
    assert body["is_leaf"] is True


def test_staff_cannot_create_top_level_node(staff_client):
    resp = staff_client.post("/api/nodes", json={"name": "新頂層業務"})
    assert resp.status_code == 403


def test_staff_can_create_child_under_own_node(admin_client, staff_client, staff_user):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]}).json()
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": staff_user.id, "role": "primary"},
    )

    resp = staff_client.post(
        "/api/nodes", json={"name": "社區宣導細項", "parent_id": leaf["id"]}
    )
    assert resp.status_code == 201
    assert resp.json()["parent_id"] == leaf["id"]

    # 原本的葉節點現在有子節點了，就不再是葉節點
    nodes = {n["id"]: n for n in admin_client.get("/api/nodes").json()}
    assert nodes[leaf["id"]]["is_leaf"] is False


def test_staff_cannot_create_child_under_unrelated_node(admin_client, staff_client):
    top = admin_client.post("/api/nodes", json={"name": "槍砲業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "查緝面", "parent_id": top["id"]}).json()

    # chen 完全沒被指派到這個節點或其祖先
    resp = staff_client.post("/api/nodes", json={"name": "細項", "parent_id": leaf["id"]})
    assert resp.status_code == 403


def test_rename_requires_admin(admin_client, staff_client):
    node = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()

    resp = staff_client.patch(f"/api/nodes/{node['id']}/rename", json={"name": "改名"})
    assert resp.status_code == 403

    resp = admin_client.patch(f"/api/nodes/{node['id']}/rename", json={"name": "改名"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "改名"


def test_rename_writes_changelog(admin_client):
    node = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    admin_client.patch(f"/api/nodes/{node['id']}/rename", json={"name": "詐欺防制業務"})

    log = admin_client.get("/api/changelog").json()
    rename_entries = [e for e in log if e["node_id"] == node["id"] and e["action"] == "rename"]
    assert len(rename_entries) == 1
    assert "詐欺防制業務" in rename_entries[0]["detail"]
