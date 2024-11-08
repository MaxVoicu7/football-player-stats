FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
  chromium \
  chromium-driver \
  xvfb \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

ENV CHROME_OPTIONS="--headless --no-sandbox --disable-dev-shm-usage"

EXPOSE 8000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
