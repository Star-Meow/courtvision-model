# 推論環境。訓練不進 Docker，本檔只打包推論與 API。
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# OpenCV 系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 先裝依賴，利用 layer cache
COPY inference/requirements.txt ./inference/requirements.txt
RUN pip install -r inference/requirements.txt

COPY inference/ ./inference/
COPY api/ ./api/

# 權重以 volume 掛載，不寫進 image
VOLUME ["/app/weights"]

ENV WEIGHTS_PATH=/app/weights/player_only_v1.pt \
    MODEL_VERSION=player_only_v1 \
    FLASK_PORT=5000

EXPOSE 5000

CMD ["python", "-m", "api.app"]
