"""YOLOv7 偵測器：第一層（模型原生）→ 第二層（中繼格式）。

三層輸出分離，本模組只負責到第二層：

  1. 模型原生  YOLOv7 raw detection   [[x1, y1, x2, y2, conf, class_id], ...]
  2. 中繼格式  to_intermediate()       dict(bbox, center, confidence, class_id, class_name)
  3. API 契約  由 api/app.py 組裝      加入 track_id 與場地座標

類別清單固定為 ['player']，class_id 恆為 0；球員身份由 ByteTrack 在執行時分配，
模型不負責身份辨識。
"""

import os

CLASSES = ("player",)
DEFAULT_CONF = 0.25
DEFAULT_IOU = 0.45


class ModelNotAvailable(RuntimeError):
    """權重或依賴尚未就緒（階段 1 尚未完成時會發生）。"""


class Detector:
    """YOLOv7 偵測器。

    weights_path 指向 weights/ 下的權重（不進 Git，見 .gitignore）。
    """

    def __init__(self, weights_path, device="cpu", conf_thres=DEFAULT_CONF, iou_thres=DEFAULT_IOU):
        self.weights_path = weights_path
        self.device = device
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self._model = None

    @property
    def loaded(self):
        return self._model is not None

    def load(self):
        """載入 YOLOv7 權重。"""
        if not self.weights_path or not os.path.exists(self.weights_path):
            raise ModelNotAvailable(f"weights not found: {self.weights_path}")
        try:
            import torch  # noqa: F401  (延遲 import，避免未安裝時 import 失敗)
        except ImportError as exc:
            raise ModelNotAvailable("torch not installed") from exc
        # TODO(stage-1): 接上 YOLOv7 model 定義與權重載入。
        raise ModelNotAvailable("stage 1 detection not yet implemented")

    def detect(self, image):
        """輸入 BGR / RGB numpy image，回傳中繼格式偵測結果（第二層）。"""
        if not self.loaded:
            self.load()
        # TODO(stage-1): 前處理 → YOLOv7 推論 → NMS → to_intermediate()
        raise ModelNotAvailable("stage 1 detection not yet implemented")

    @staticmethod
    def to_intermediate(raw_detections):
        """第一層 → 第二層：[[x1, y1, x2, y2, conf, cls], ...] → dict 序列。"""
        results = []
        for x1, y1, x2, y2, conf, cls_id in raw_detections:
            cls_id = int(cls_id)
            results.append(
                {
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "center": [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                    "confidence": float(conf),
                    "class_id": cls_id,
                    "class_name": CLASSES[cls_id] if cls_id < len(CLASSES) else "unknown",
                }
            )
        return results
