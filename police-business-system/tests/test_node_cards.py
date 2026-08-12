def test_new_users_get_colors_in_creation_order(admin_client, staff_user, other_staff_user):
    from app.services.colors import STAFF_PALETTE

    users = {u["username"]: u for u in admin_client.get("/api/users").json()}
    # admin_user 是第一個建立（conftest 的 admin_client fixture 觸發），staff/other 依序在後
    assert users["admin"]["color"] == STAFF_PALETTE[0]
    assert users["chen"]["color"] == STAFF_PALETTE[1]
    assert users["wang"]["color"] == STAFF_PALETTE[2]


def test_cards_only_include_leaf_nodes(admin_client):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]}).json()

    cards = admin_client.get("/api/nodes/cards").json()
    card_ids = {c["id"] for c in cards}
    assert leaf["id"] in card_ids
    assert top["id"] not in card_ids


def test_card_shows_breadcrumb_primary_and_support(admin_client, staff_user, other_staff_user):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]}).json()
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": staff_user.id, "role": "primary"},
    )
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": other_staff_user.id, "role": "support"},
    )

    cards = admin_client.get("/api/nodes/cards").json()
    card = next(c for c in cards if c["id"] == leaf["id"])
    assert card["breadcrumb"] == "詐欺業務"
    assert card["primary_user"]["username"] == "chen"
    assert card["support_names"] == ["王小華"]


def test_unassigned_card_has_no_primary_user(admin_client):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]}).json()

    cards = admin_client.get("/api/nodes/cards").json()
    card = next(c for c in cards if c["id"] == leaf["id"])
    assert card["primary_user"] is None
    assert card["support_names"] == []
    assert card["award_status"] is None
