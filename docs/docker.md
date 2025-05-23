# Docker Setup for Poly Micro Manager Backend

This guide explains how to use Docker to run the Poly Micro Manager backend.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

1. Build and start the containers:

```bash
docker-compose up -d
```

2. Access the API:
   - API: http://localhost:8000
   - Swagger Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

3. Stop the containers:

```bash
docker-compose down
```

## Configuration

The Docker setup includes:

1. **Backend Container**: Runs the FastAPI application
2. **MongoDB Container**: Provides the database
3. **Redis Container**: Provides caching functionality for improved performance

### Environment Variables

The following environment variables can be modified in the `docker-compose.yml` file:

| Variable      | Default                | Description                        |
|--------------|------------------------|------------------------------------|  
| MONGO_URI     | mongodb://mongodb:27017 | MongoDB connection string          |
| MONGO_DB      | Lab2                    | MongoDB database name              |
| HOST          | 0.0.0.0                 | Host to bind the server to         |
| PORT          | 8000                    | Port to run the server on          |
| RELOAD        | False                   | Enable auto-reload for development |
| ENV           | production              | Environment (development/production) |
| REDIS_HOST    | redis                   | Redis host name                    |
| REDIS_PORT    | 6379                    | Redis port                         |
| CACHE_ENABLED | True                    | Enable/disable Redis caching       |

## Frontend Integration

To connect your frontend to the containerized backend:

1. Make sure your frontend is configured to make API requests to `http://localhost:8000/api`
2. The backend has CORS configured to accept requests from common frontend development ports

## Troubleshooting

### Cannot connect to the backend

- Ensure the containers are running: `docker-compose ps`
- Check container logs: `docker-compose logs backend`
- Verify the port mapping: `docker-compose port backend 8000`

### Database connection issues

- Check MongoDB container logs: `docker-compose logs mongodb`
- Verify MongoDB is running: `docker exec -it poly-micro-mongodb mongo`

### Redis caching issues

- Check Redis container logs: `docker-compose logs redis`
- Verify Redis is running: `docker exec -it poly-micro-redis redis-cli ping`
- Test Redis connectivity from backend: `docker exec -it poly-micro-backend redis-cli -h redis ping`
- You can disable caching by setting `CACHE_ENABLED=False` in the docker-compose.yml file

## Building a Production Image

To build a standalone production image:

```bash
docker build -t poly-micro-backend:latest .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e MONGO_URI=your_mongo_uri \
  -e CACHE_ENABLED=False \
  poly-micro-backend:latest
```

Or with Redis:

```bash
# First start Redis
docker run --name redis -d redis:alpine

# Then start the backend with Redis connection
docker run -p 8000:8000 \
  -e MONGO_URI=your_mongo_uri \
  -e REDIS_HOST=redis \
  -e CACHE_ENABLED=True \
  --link redis:redis \
  poly-micro-backend:latest
```

## Deployment Considerations

For production deployment:

1. Use a specific MongoDB connection string instead of the local container
2. Set specific CORS origins instead of wildcards
3. Consider using Docker Swarm or Kubernetes for orchestration
4. Set up proper logging and monitoring
5. Configure Redis persistence for durability
6. Consider using Redis Sentinel or Redis Cluster for high availability
7. Monitor cache hit/miss rates to optimize caching strategies
