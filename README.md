# CourtVision Model

> 將籃球比賽影片逐幀轉換為球員在場地座標上的位置，透過 Flask API 輸出。本專案只負責模型端，不處理前端、UI 或資料庫。

## 專案簡介

CourtVision-model 是 CourtVision 系統的模型端。輸入為比賽影片的逐幀影像，輸出為球員在場地座標系上的位置序列，以 Flask API 對外提供。

模型端只做四件事：**偵測、追蹤、座標映射、API 輸出**。YOLOv7 只認「人」，球員身份由 ByteTrack 在執行時分配 `track_id`；模型不負責身份辨識、背號或持球判定。

## 核心流程

```text
輸入幀 → YOLOv7 偵測 → ByteTrack 追蹤 → 座標映射 → Flask API 輸出
```

| 階段 | 職責 | 狀態 |
| --- | --- | --- |
| YOLOv7 偵測 | 輸出 bbox 與信心度，類別只有 `player` | 階段 1，待開發 |
| ByteTrack 追蹤 | 跨幀維持 `track_id` | 階段 1.5，待開發 |
| 座標映射 | 像素座標 → 場地座標系 | 待開發 |
| Flask API | 三層輸出分離，契約化 JSON | 骨架已建立 |

## 技術棧

| 元件 | 選擇 |
| --- | --- |
| 偵測 | YOLOv7 |
| 影像 | OpenCV |
| 追蹤 | ByteTrack |
| API | Flask |
| 訓練環境 | conda / venv |
| 推論環境 | Docker |

## 目錄結構

```text
courtvision-model/
├── training/          # 研究軌道：資料、訓練腳本、實驗記錄
├── inference/         # 推論核心：載入權重、產出中繼格式
├── api/               # Flask 服務
├── weights/           # 權重，一律 .gitignore，不進 Git
├── contracts/         # 輸出契約文件
├── tests/
├── Dockerfile         # 推論環境（訓練不進 Docker）
├── AGENTS.md
└── README.md
```

研究與工程分離：`training/` 變動頻繁，`inference/` 與 `api/` 穩定，不要把實驗性修改寫進推論軌道。

## 安裝與執行

### 訓練（conda / venv，不進 Docker）

```bash
conda create -n courtvision python=3.9 -y
conda activate courtvision
pip install -r training/requirements.txt

python training/train.py \
  --weights yolov7.pt \
  --data training/dataset.yaml \
  --epochs 100 \
  --batch-size 16 \
  --name player_only_v1
```

### 推論與 API（Docker）

```bash
docker compose up --build

# 或手動指定權重路徑
docker build -t courtvision-model .
docker run --gpus all -p 5000:5000 \
  -v "$PWD/weights:/app/weights:ro" \
  courtvision-model
```

權重以 volume 掛載，不寫進 image，換模型不需重建。

### 本機開發 API

```bash
pip install -r inference/requirements.txt -r requirements-dev.txt
python -m api.app
```

### 測試與監控

```bash
python -m pytest tests/
tensorboard --logdir training/runs
```

## API 端點

| 路由 | 方法 | 說明 |
| --- | --- | --- |
| `/healthz` | GET | 健康檢查 |
| `/v1/model-info` | GET | 模型版本、類別清單 |
| `/v1/positions` | GET | 回傳偵測結果 |
| `/v1/predict` | POST | 單張圖片推論（研究用） |

`/v1/predict` 僅供研究與 debug，不建議對 system 開放。

## 輸出契約

三層輸出分離，層與層之間不準跳過，詳見 [contracts/output-contract.md](contracts/output-contract.md)：

1. **模型原生**：YOLOv7 raw detection `[x1, y1, x2, y2, conf, class_id]`
2. **中繼格式**：`inference/detector.py` 產出，含 bbox、中心點、信心度、類別
3. **API 契約**：`api/app.py` 組裝，加入 `track_id` 與場地座標

契約不變是硬原則：加類別時只能擴充，不能改變既有欄位語意。

## 與 system 整合

- system 透過 `/v1/positions` 取得逐幀位置，**只認 `track_id`，不依賴輸出順序**。
- system 啟動時呼叫 `/v1/model-info` 確認模型版本與類別清單；加類別時向後相容。
- `/healthz` 供反向代理或编排平台做健康檢查。
- 部署為 Docker container，權重 volume 掛載，換模型不需重建 image。

## 開發階段

| 階段 | 任務 | 狀態 |
| --- | --- | --- |
| 1 | 球員偵測（`['player']`） | 待開發 |
| 1.5 | ByteTrack 追蹤 | 待開發 |
| 2 | 背號辨識 | 待開發 |
| 3 | 籃球偵測 | 待開發 |
| 4 | 持球者判定 | 待開發 |

目前聚焦階段 1 與 1.5。訓練驗收指標：mAP@0.5 > 0.8、Precision > 0.8、Recall > 0.8，以 TensorBoard 監控。
