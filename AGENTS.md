# AGENTS.md

> 給在本 repo 工作的 AI agent 與人類協作者：專案定位、設計原則、決策記錄與地雷區。

## 專案定位與邊界

CourtVision-model 是 CourtVision 系統的**模型端**：影片逐幀 → 球員場地座標 → Flask API。

**本專案負責**：YOLOv7 訓練與推論、OpenCV 前後處理、ByteTrack 整合、座標映射、Flask API、權重管理。

**本專案不負責**：前端、session、資料庫、system 內部邏輯、權重的 Git 儲存。

看到「幫前端加欄位」「改 system 業務邏輯」這類需求，先退回，不要在這個 repo 動手。

## 設計原則

1. **契約不變**：加類別時向後相容，只能擴充不能改欄位語意。改契約前先改 `contracts/`。
2. **輸出順序不重要**：前端認 `track_id`，任何地方都不要假設回傳陣列的順序。
3. **三層輸出分離**：模型原生 → 中繼格式 → API 契約，層與層之間不準跳過。
4. **研究與工程分離**：實驗寫在 `training/`；`inference/` 與 `api/` 只放穩定程式碼。
5. **訓練不進 Docker，推論進 Docker。**
6. **權重不進 Git**（`weights/` 恆為 ignored，用 DVC / S3 / Git LFS 控管）。

## 標註決策記錄

| 決策 | 內容 |
| --- | --- |
| 類別 | 固定 `['player']`，YOLO TXT 格式，`class_id` 恆為 0 |
| 不標 | 背號、籃球、裁判、觀眾 — 延後到階段 2 / 3 |
| 種子資料 | 30～50 張人工標註，覆蓋不同光照、遮擋、角度、球員數量 |
| 迭代 | 種子 → 初始模型 → 批量預標註 → **人工審核修正** → 重訓 |
| 工具 | Label Studio（首選）或 X-AnyLabeling |
| 預標註 | 一律人工校驗，不預設正確 |

## 開發階段與狀態

| 階段 | 任務 | 狀態 | 關鍵變化 |
| --- | --- | --- | --- |
| 1 | 球員偵測 | 待開發 | `['player']` 種子標註 + 訓練 |
| 1.5 | ByteTrack 追蹤 | 待開發 | 輸出加 `track_id` |
| 2 | 背號辨識 | 待開發 | 裁切球員框 + CNN 分類器 |
| 3 | 籃球偵測 | 待開發 | `nc` 改 2，混合舊資料 fine-tune |
| 4 | 持球者判定 | 待開發 | IoU / 距離邏輯 |

**目前聚焦階段 1 與 1.5。** 驗收指標：mAP@0.5 > 0.8、Precision > 0.8、Recall > 0.8（TensorBoard 監控）。

## 常見陷阱

- **權重 commit 進 Git**：`weights/` 與 `*.pt` 都在 `.gitignore`，不要 `git add -f`。
- **訓練跑 Docker**：方向相反。訓練用 conda / venv，只有推論進 Docker。
- **預標註沒校驗就進訓練集**：錯誤標籤直接污染模型。
- **加類別時不混合舊資料**：只用新資料 fine-tune 會災難性遺忘，連 player 都忘掉。
- **fine-tune 用高 learning rate**：從階段 1 權重出發要降 lr。
- **依賴 API 回傳順序**：契約明訂順序不重要，只認 `track_id`。
- **在 `inference/`、`api/` 做實驗性修改**：請到 `training/`。
- **改 `class_id` 語意**：破壞契約，等於砸掉 system 整合。

## 指令速查

```bash
# 訓練（本機 conda / venv）
python training/train.py --weights yolov7.pt --data training/dataset.yaml \
  --epochs 100 --batch-size 16 --name player_only_v1

# TensorBoard
tensorboard --logdir training/runs

# 本機 API
python -m api.app

# Docker 推論
docker compose up --build

# 測試
python -m pytest tests/
```

## 與 system 協作方式

- **唯一介面是 API 契約**，system 不應直接 import 推論程式碼。
- **唯一身份鍵是 `track_id`**；ID 中斷或重號的處理歸 system。
- 加類別前先更新 `contracts/output-contract.md` 與 `/v1/model-info`，保持向後相容。
- 模型版本透過 `/v1/model-info` 暴露，換權重不需改 system。

## 未來擴充方向

從階段 1 權重 fine-tune 加入新類別：**降低 learning rate + 混合舊資料**，避免災難性遺忘。舊資料保留在 `training/data/`，不要刪。

- **階段 2 背號辨識**：裁切球員框 → CNN 分類器，獨立於 YOLO。
- **階段 3 籃球偵測**：`nc` 改為 2，與舊 player 資料混合 fine-tune。
- **階段 4 持球者判定**：用 IoU / 球與球員距離推導，可放在推論後處理。
