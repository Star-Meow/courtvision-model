"""CourtVision 模型端 Flask API。

端點：
  GET  /healthz         健康檢查
  GET  /v1/model-info   模型版本與類別清單
  GET  /v1/positions    回傳偵測結果（逐幀位置）
  POST /v1/predict      單張圖片推論（研究用）

輸出順序不重要，消費端一律認 track_id。
"""

import os
import sys

# 支援 python api/app.py 與 python -m api.app 兩種啟動方式。
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import numpy as np  # noqa: E402
from flask import Flask, jsonify, request  # noqa: E402

from inference.detector import CLASSES, Detector, ModelNotAvailable  # noqa: E402

MODEL_VERSION = os.environ.get("MODEL_VERSION", "player_only_v1")
WEIGHTS_PATH = os.environ.get("WEIGHTS_PATH", os.path.join("weights", "player_only_v1.pt"))
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))

app = Flask(__name__)
_detector = Detector(WEIGHTS_PATH)


@app.get("/healthz")
def healthz():
    """liveness：process 活著即 200；weights 是否就緒另外反映在欄位。"""
    return jsonify(
        {
            "status": "ok",
            "version": MODEL_VERSION,
            "weights_ready": bool(WEIGHTS_PATH) and os.path.exists(WEIGHTS_PATH),
        }
    )


@app.get("/v1/model-info")
def model_info():
    return jsonify(
        {
            "model": "courtvision-yolov7",
            "version": MODEL_VERSION,
            "classes": list(CLASSES),
            "tracker": "bytetrack",
        }
    )


@app.get("/v1/positions")
def positions():
    # TODO(stage-1.5): 接上影片 / 逐幀來源與 ByteTrack，輸出帶 track_id 的位置。
    return jsonify(
        {
            "frame_id": None,
            "positions": [],
            "note": "stage 1 / 1.5 not yet implemented",
        }
    )


@app.post("/v1/predict")
def predict():
    if "image" not in request.files:
        return jsonify({"error": "missing 'image' file"}), 400

    try:
        import cv2
    except ImportError:
        return jsonify({"error": "opencv not installed"}), 500

    file = request.files["image"]
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify({"error": "cannot decode image"}), 400

    try:
        detections = _detector.detect(image)
    except ModelNotAvailable as exc:
        return jsonify({"error": str(exc)}), 501

    return jsonify({"detections": detections})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT)
