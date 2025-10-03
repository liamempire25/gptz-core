FROM python:3.11-slim

# install system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev git curl jq

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
