from fastapi import APIRouter
from app.api.routes import projects, services, logs, metrics, service_logs

api_router = APIRouter()

# Include all the routers
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(service_logs.router, prefix="/service-logs", tags=["Service Logs"])
