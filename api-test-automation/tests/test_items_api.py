import pytest


def create(api, name="Widget", quantity=5):
    return api.post("/items", json={"name": name, "quantity": quantity})


# ---------- smoke ----------
@pytest.mark.smoke
def test_empty_list_on_fresh_server(api):
    r = api.get("/items")
    assert r.status_code == 200
    assert r.json() == []


# ---------- create ----------
def test_create_returns_201_and_item(api):
    r = create(api)
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "Widget", "quantity": 5}


def test_ids_increment(api):
    assert create(api).json()["id"] == 1
    assert create(api, "Gadget").json()["id"] == 2


def test_name_is_trimmed(api):
    assert create(api, name="  Bolt  ").json()["name"] == "Bolt"


def test_zero_quantity_is_allowed(api):
    assert create(api, quantity=0).status_code == 201


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"quantity": 1}, "name"),
        ({"name": "", "quantity": 1}, "name"),
        ({"name": "   ", "quantity": 1}, "name"),
        ({"name": 123, "quantity": 1}, "name"),
        ({"name": "x"}, "quantity"),
        ({"name": "x", "quantity": -1}, ">= 0"),
        ({"name": "x", "quantity": "5"}, "integer"),
        ({"name": "x", "quantity": 1.5}, "integer"),
        ({"name": "x", "quantity": True}, "integer"),  # bool is an int in Python: classic edge case
    ],
)
def test_invalid_payloads_rejected(api, payload, message):
    r = api.post("/items", json=payload)
    assert r.status_code == 400
    assert message in r.json()["error"]


def test_invalid_json_rejected(api):
    r = api.post("/items", data="{not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json()["error"] == "invalid JSON"


def test_non_object_body_rejected(api):
    assert api.post("/items", json=[1, 2, 3]).status_code == 400


# ---------- read ----------
def test_get_created_item(api):
    created = create(api).json()
    r = api.get(f"/items/{created['id']}")
    assert r.status_code == 200
    assert r.json() == created


def test_list_contains_created_items(api):
    create(api, "A")
    create(api, "B")
    names = [i["name"] for i in api.get("/items").json()]
    assert names == ["A", "B"]


@pytest.mark.parametrize("path", ["/items/999", "/items/abc", "/items/1/extra", "/nope"])
def test_unknown_routes_return_404(api, path):
    assert api.get(path).status_code == 404


# ---------- delete ----------
def test_delete_then_get_is_404(api):
    item_id = create(api).json()["id"]
    assert api.delete(f"/items/{item_id}").status_code == 204
    assert api.get(f"/items/{item_id}").status_code == 404


def test_delete_twice_second_is_404(api):
    item_id = create(api).json()["id"]
    api.delete(f"/items/{item_id}")
    assert api.delete(f"/items/{item_id}").status_code == 404


def test_deleted_id_is_not_reused(api):
    first = create(api).json()["id"]
    api.delete(f"/items/{first}")
    assert create(api).json()["id"] == first + 1


# ---------- response format ----------
def test_json_content_type(api):
    assert api.get("/items").headers["Content-Type"] == "application/json"
