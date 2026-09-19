# 訓練資料

YOLO TXT 格式，目錄編排遵循 YOLOv7 慣例：

```text
training/data/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

- 圖片與標籤同名，副檔分別為 `.jpg` / `.txt`。
- 每行 `class_id cx cy w h`，座標正規化到 `[0, 1]`。
- `class_id` 恆為 `0`（player）。

## 種子資料

階段 1 先人工標註 30～50 張種子圖片，挑選原則：**覆蓋不同光照、遮擋、角度、球員數量**。

## 預標註迭代

```text
人工標註種子 → 訓練初始模型 → 批量預標註 → 人工審核修正 → 加入訓練集重訓
```

預標註結果**必須人工校驗**，不要預設正確。標註工具用 Label Studio（首選）或 X-AnyLabeling。

## 圖片不進 Git

`images/` 與 `labels/` 已在 `.gitignore`，資料集用 DVC / S3 等外部儲存控管。

## 加類別時

保留舊資料，新類別往後編號，混合舊資料 fine-tune 並降低 learning rate，避免災難性遺忘。
