FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
RUN useradd -r -u 10001 app
USER 10001
CMD ["uvicorn","meta_business.api.main:app","--host","0.0.0.0","--port","8080"]
