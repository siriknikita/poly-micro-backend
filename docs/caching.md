# Caching Implementation

The Poly Micro Manager backend uses Redis as a caching layer to improve performance and reduce database load. This document explains how caching is implemented and how to configure it.

## Architecture

The caching layer sits between the repository layer and the database, storing frequently accessed data to reduce database queries:

```
API Controllers → Services → Repositories → Cache → Database
```

## Cache Configuration

Caching is configured via environment variables:

| Variable      | Default | Description                      |
|---------------|---------|----------------------------------|
| CACHE_ENABLED | True    | Enable/disable the caching layer |
| REDIS_HOST    | redis   | Redis server hostname            |
| REDIS_PORT    | 6379    | Redis server port                |

## Cached Operations

The following repository methods are cached:

### Project Repository
- `get_all_projects` (TTL: 300s)
- `get_project_by_id` (TTL: 300s)

### Service Repository
- `get_all_services` (TTL: 300s)
- `get_service_by_id` (TTL: 300s)
- `get_services_by_project` (TTL: 300s)

### Log Repository
- `get_all_logs` (TTL: 300s)
- `get_logs_by_project` (TTL: 300s)
- `get_logs_by_service` (TTL: 300s)

### Metrics Repository
- `get_all_cpu_data` (TTL: 300s)
- `get_cpu_data_by_project` (TTL: 300s)
- `get_cpu_data_by_service` (TTL: 300s)
- `get_cpu_entry_by_id` (TTL: 300s)

## Cache Invalidation

Cache is automatically invalidated when data is modified through the following operations:
- Create operations
- Update operations
- Delete operations

## Implementation Details

Caching is implemented through Python decorators applied to repository methods:

```python
# Example of caching implementation
@cached(ttl=300, prefix="projects:all")
async def get_all_projects(self) -> List[Dict[str, Any]]:
    """Get all projects with caching"""
    projects = await self.find_all()
    return projects
```

## Monitoring Cache Performance

Currently, there is no built-in monitoring for cache hit/miss rates. For production environments, it's recommended to:

1. Add cache hit/miss metrics
2. Monitor Redis memory usage
3. Adjust TTL values based on access patterns

## Troubleshooting

If you encounter issues with caching:

1. Verify Redis is running: `docker exec -it poly-micro-redis redis-cli ping`
2. Check Redis connectivity: `docker exec -it poly-micro-backend redis-cli -h redis ping`
3. Disable caching temporarily: Set `CACHE_ENABLED=False` in environment variables
4. Clear Redis cache: `docker exec -it poly-micro-redis redis-cli FLUSHALL`
