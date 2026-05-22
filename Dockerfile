FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 8000 7860
ENV API_BASE_URL=http://127.0.0.1:8000

CMD ["/bin/sh", "-c", "./startup.sh"]
