FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y     build-essential default-libmysqlclient-dev pkg-config &&     rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations then start
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
