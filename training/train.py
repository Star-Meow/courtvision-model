"""球員偵測模型訓練腳本（階段 1）。

類別固定為 ['player']，class_id 恆為 0。訓練在本機以 conda / venv 執行，不進 Docker。

用法：

  python training/train.py \
      --weights yolov7.pt \
      --data training/dataset.yaml \
      --epochs 100 \
      --batch-size 16 \
      --name player_only_v1

驗收指標：mAP@0.5 > 0.8、Precision > 0.8、Recall > 0.8（TensorBoard 監控）。
標註採「種子 + 預標註迭代」，預標註結果必須人工校驗，詳見 training/data/README.md。
"""

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="CourtVision stage-1 player detection training")
    parser.add_argument("--weights", default="yolov7.pt", help="預訓練權重起點")
    parser.add_argument("--data", default="training/dataset.yaml", help="YOLO dataset config")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--device", default="", help="cuda device 或 cpu，空字串為自動")
    parser.add_argument("--name", default="player_only_v1", help="實驗名稱，輸出至 training/runs/<name>")
    return parser.parse_args()


def main():
    args = parse_args()
    print("[courtvision] stage-1 player detection training")
    print(
        f"[courtvision] weights={args.weights} data={args.data} "
        f"epochs={args.epochs} batch={args.batch_size} img={args.img_size} name={args.name}"
    )
    # TODO(stage-1): 接上 YOLOv7 train.py，輸出至 training/runs/<name>。
    raise SystemExit("YOLOv7 training pipeline not yet wired in (stage 1 待開發)")


if __name__ == "__main__":
    main()
