"""API 契約基本測試。"""

import pytest

from api.app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_healthz_is_live(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert "weights_ready" in body


def test_model_info_lists_player_only(client):
    resp = client.get("/v1/model-info")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["classes"] == ["player"]
    assert body["version"]
    assert body["tracker"] == "bytetrack"


def test_positions_contract_shape(client):
    resp = client.get("/v1/positions")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "positions" in body
    # 輸出順序不重要，消費端只認 track_id；這裡只驗證欄位存在。


def test_predict_requires_image(client):
    resp = client.post("/v1/predict")
    assert resp.status_code == 400
