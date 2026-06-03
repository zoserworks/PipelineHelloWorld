"""
zoser-dummy — App de teste para validar a esteira GitOps
Endpoints:
  GET /          → health check
  GET /metrics   → métricas para o Prometheus
  GET /info      → info da app
"""
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import os

app = FastAPI(title="zoser-dummy", version="0.1.0")

# ------------------------------------------------------------
# Métricas Prometheus
# ------------------------------------------------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requisições HTTP",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Latência das requisições HTTP",
    ["endpoint"]
)

APP_INFO = Gauge(
    "app_info",
    "Informações da aplicação",
    ["version", "environment"]
)

APP_INFO.labels(
    version=os.getenv("APP_VERSION", "0.1.0"),
    environment=os.getenv("APP_ENV", "production")
).set(1)

# ------------------------------------------------------------
# Middleware para contar requisições automaticamente
# ------------------------------------------------------------
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=request.url.path
        ).observe(duration)

        return response

app.add_middleware(MetricsMiddleware)

# ------------------------------------------------------------
# Rotas
# ------------------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "app": "zoser-dummy",
        "version": os.getenv("APP_VERSION", "0.1.0")
    }

@app.get("/info")
def info():
    return {
        "app": "zoser-dummy",
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "environment": os.getenv("APP_ENV", "production"),
        "deployed_by": "GitHub Actions + zoserworks runner"
    }

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )