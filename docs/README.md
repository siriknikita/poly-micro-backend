# Poly Micro Manager Backend

Welcome to the Poly Micro Manager Backend Documentation!

This documentation covers all aspects of the Poly Micro Manager backend system, a microservices management platform designed for monitoring and controlling distributed applications.

## Key Features

- RESTful API for microservices management
- MongoDB data persistence
- Redis caching layer for improved performance
- Containerized deployment with Docker
- Comprehensive logging system

## Getting Started

- [API Documentation](/api.md) - Explore the available API endpoints
- [Architecture](/ARCHITECTURE.md) - Understand the system design
- [Docker Setup](/DOCKER.md) - Learn how to run the application using Docker
- [Caching Implementation](/caching.md) - Details on the Redis caching layer
- [Development Guide](/development.md) - Guide for developers

## Quick Start

To get started with the Poly Micro Manager backend:

```bash
# Clone the repository
git clone https://github.com/siriknikita/university-3-course.git

# Navigate to the backend directory
cd poly-micro-manager/poly-micro-backend

# Run with Docker
docker-compose up -d
```

The API will be available at http://localhost:8000, with Swagger documentation at http://localhost:8000/docs.
