from fastapi import Depends
from app.db.database import get_database
from app.db.repositories.project_repository import ProjectRepository
from app.db.repositories.service_repository import ServiceRepository
from app.db.repositories.log_repository import LogRepository
from app.db.repositories.metrics_repository import MetricsRepository
from app.db.repositories.logs_collection_repository import LogsCollectionRepository
from app.services.project_service import ProjectService
from app.services.service_service import ServiceService
from app.services.log_service import LogService
from app.services.metrics_service import MetricsService
from app.services.service_logs_service import ServiceLogsService
from app.services.test_service import TestService

# Repository dependencies
def get_project_repository():
    return ProjectRepository(get_database())

def get_service_repository():
    return ServiceRepository(get_database())

def get_log_repository():
    return LogRepository(get_database())

def get_metrics_repository():
    return MetricsRepository(get_database())

def get_logs_collection_repository():
    return LogsCollectionRepository(get_database())

# Service dependencies
def get_project_service(
    project_repository: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    # We'll initialize without service_service to avoid circular dependencies
    # The actual service_service will be injected at runtime by FastAPI
    return ProjectService(project_repository)

def get_service_service(
    service_repository: ServiceRepository = Depends(get_service_repository),
    project_repository: ProjectRepository = Depends(get_project_repository)
) -> ServiceService:
    return ServiceService(service_repository, project_repository)

def get_log_service(
    log_repository: LogRepository = Depends(get_log_repository)
) -> LogService:
    return LogService(log_repository)

def get_metrics_service(
    metrics_repository: MetricsRepository = Depends(get_metrics_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    service_repository: ServiceRepository = Depends(get_service_repository)
) -> MetricsService:
    return MetricsService(metrics_repository, project_repository, service_repository)

def get_service_logs_service(
    logs_repository: LogsCollectionRepository = Depends(get_logs_collection_repository)
) -> ServiceLogsService:
    return ServiceLogsService(logs_repository)

def get_test_service(
    log_service: LogService = Depends(get_log_service)
) -> TestService:
    return TestService(log_service)
