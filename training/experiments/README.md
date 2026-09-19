# 實驗記錄

每個實驗一個子目錄或一份 markdown，記錄：

- 實驗名稱（對應訓練的 `--name`）
- 訓練資料版本與種子圖片數
- 超參數（epochs、batch size、learning rate）
- 驗收指標：mAP@0.5、Precision、Recall
- 權重位置（`weights/`，不進 Git）

## 驗收門檻

| 指標 | 目標 |
| --- | --- |
| mAP@0.5 | > 0.8 |
| Precision | > 0.8 |
| Recall | > 0.8 |

以 TensorBoard 監控：`tensorboard --logdir training/runs`。
