#!/bin/bash
set -e

echo "Starting Poly Micro Manager Backend..."

# Wait for Redis if enabled
if [ "$CACHE_ENABLED" = "True" ] || [ "$CACHE_ENABLED" = "true" ] || [ "$CACHE_ENABLED" = "1" ]; then
    echo "Cache is enabled, checking Redis connection..."
    
    # Function to check if Redis is available
    check_redis() {
        redis-cli -h $REDIS_HOST -p $REDIS_PORT ping >/dev/null 2>&1
        return $?
    }
    
    # Wait for Redis to be ready
    retry_count=0
    max_retries=30
    retry_interval=1
    
    until check_redis || [ $retry_count -eq $max_retries ]; do
        echo "Waiting for Redis to be ready... ($((retry_count+1))/$max_retries)"
        retry_count=$((retry_count+1))
        sleep $retry_interval
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "WARNING: Could not connect to Redis. Cache will be disabled."
        export CACHE_ENABLED=False
    else
        echo "Successfully connected to Redis."
    fi
fi

# Run the application
exec python run.py
