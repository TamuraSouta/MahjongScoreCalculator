# 使用するベースイメージ
FROM python:3.8-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なパッケージファイルをコピー
COPY requirements.txt /app/requirements.txt

# パッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . /app

# コンテナがリッスンするポート番号を指定
EXPOSE 8501

# コンテナ起動時に実行されるコマンド
CMD ["streamlit", "run", "main.py"]
