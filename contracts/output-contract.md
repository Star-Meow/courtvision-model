# 輸出契約

三層輸出分離：**模型原生 → 中繼格式 → API 契約**。層與層之間不準跳過；
要改動輸出，先改本文件，再改程式，保持 system 整合向後相容。

## 第 1 層：模型原生（YOLOv7）

NMS 後的 raw detection：

```text
[[x1, y1, x2, y2, confidence, class_id], ...]
```

- 座標為像素值，未正規化。
- `class_id` 目前恆為 `0`（player）。

## 第 2 層：中繼格式（inference/detector.py）

```json
{
  "detections": [
    {
      "bbox": [x1, y1, x2, y2],
      "center": [cx, cy],
      "confidence": 0.92,
      "class_id": 0,
      "class_name": "player"
    }
  ]
}
```

`center` 為 bbox 中心點，是座標映射的輸入。

## 第 3 層：API 契約（api/app.py）

`GET /v1/positions`：

```json
{
  "frame_id": 123,
  "timestamp": 4.16,
  "positions": [
    {
      "track_id": 7,
      "bbox": [x1, y1, x2, y2],
      "court_xy": [10.5, 3.2],
      "confidence": 0.92
    }
  ]
}
```

- `track_id` 由 ByteTrack 在執行時分配，**輸出順序不重要**，消費端只認 `track_id`。
- `court_xy` 為場地座標；座標映射完成前為 `null`（階段 1 / 1.5 期間）。

## 向後相容

加類別（階段 3 加籃球）時：

- `class_id` 只能往後編號，`player` 恆為 `0`。
- API 只增欄位，不改既有欄位語意。
- 舊資料混合訓練，避免災難性遺忘。
