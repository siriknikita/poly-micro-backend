# Test Execution Feature Documentation

## Overview

The test execution feature enables users to run automated tests for microservices directly from the Poly Micro Manager application. This feature integrates with Docker containers running on the user's local machine to execute tests and collect results, providing a seamless testing experience for microservice applications.

## Feature Description

### Functionality

- **Run Tests On-Demand**: Users can trigger test execution for any microservice with a single click.
- **Real-Time Test Results**: Test execution results are displayed in real-time, showing test progress and outcomes.
- **Detailed Test Reports**: Comprehensive test reports show individual test results, including passed, failed, and skipped tests.
- **Console Output**: Raw console output from test execution is available for debugging.
- **Test Duration Metrics**: Performance metrics for each test, including setup, execution, and teardown times.
- **Error Details**: Detailed error information for failed tests.

### User Experience

1. From the service details view, users can click the "Run Tests" button for any microservice.
2. A modal dialog appears showing the test execution status.
3. Once tests complete, results are displayed with summary statistics and detailed test outcomes.
4. Users can expand sections to view raw test output and error details.
5. Test results can be closed, and tests can be re-run as needed.

## Technical Implementation

### Architecture

The test execution feature follows a client-server architecture:

- **Frontend (React)**: Provides the UI for triggering tests and displaying results.
- **Backend (FastAPI)**: Handles test execution requests and communicates with Docker containers.
- **Docker Integration**: Executes tests inside the relevant service containers and extracts results.

### Backend Implementation

#### Dependencies

- **Docker Python SDK**: Used to interact with Docker containers on the host machine.
- **FastAPI**: Provides the API endpoints for test execution.
- **Tarfile/Shutil**: Used for extracting test reports from Docker containers.

#### Key Components

1. **Docker Socket Mount**:
   - The backend container mounts the host's Docker socket to `/var/run/docker.sock`
   - This allows the Python application to communicate with the host's Docker daemon

2. **Test Execution Endpoint**:
   ```python
   @router.post("/run-tests/{service_id}", response_model=Dict[str, Any])
   async def run_service_tests(service_id: str, service_service: ServiceService, project_service: ProjectService)
   ```

3. **Docker Availability Check**:
   ```python
   try:
       docker_client = docker.from_env()
       docker_client.ping()
   except Exception as e:
       # Return error response if Docker is not accessible
   ```

4. **Container Execution**:
   ```python
   exec_command = ["pytest", f"/tests/{service.name}", "--json-report", "--json-report-file=/tmp/report.json"]
   exec_result = target_container.exec_run(exec_command)
   ```

5. **Report Extraction**:
   - Uses Docker's archive extraction to retrieve test reports from containers
   - Implements retry mechanism for JSON parsing to handle timing issues
   ```python
   bits, stat = target_container.get_archive('/tmp/report.json')
   with tarfile.open(temp_path) as tar:
       # Find and extract the report file
   ```

### Frontend Implementation

#### Key Components

1. **Run Tests Button**:
   ```tsx
   const RunTestsButton: React.FC<{ serviceId: string; serviceName: string }> = ({
     serviceId,
     serviceName,
   }) => {
     const { runTests, isRunning, testResult } = useRunServiceTests();
     // Implementation details
   }
   ```

2. **Test Results Modal**:
   - Displays test summary (total, passed, failed)
   - Shows detailed test output
   - Handles loading states and errors

3. **Test Duration Calculation**:
   ```tsx
   <div className="text-xs">
     {test.outcome} ({((test.call?.duration || 0) + (test.setup?.duration || 0) + (test.teardown?.duration || 0)).toFixed(3)}s)
   </div>
   ```

### Docker Configuration

1. **Backend Container Setup**:
   - The Docker Python SDK is installed in the backend container
   - Docker CLI tools are available for Docker command execution

   ```dockerfile
   # Install Docker CLI
   RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
       && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
       | tee /etc/apt/sources.list.d/docker.list > /dev/null \
       && apt-get update \
       && apt-get install -y --no-install-recommends docker-ce-cli
   ```

2. **Docker Socket Mount in docker-compose.yml**:
   ```yaml
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock  # Mount Docker socket to allow Docker API access
   ```

## Security Considerations

- The application requires access to the Docker socket, which gives it control over Docker containers on the host machine.
- This feature should only be used in environments where the user has proper permissions to access Docker containers.
- The backend validates service existence before attempting to execute tests to prevent unauthorized access.

## Error Handling

The feature includes robust error handling for various scenarios:

1. **Docker Unavailability**: If Docker is not accessible, a friendly error message guides the user.
2. **Container Not Found**: If the target container doesn't exist, a clear error is shown.
3. **Test Execution Failures**: If tests fail to execute, the error output is captured and displayed.
4. **Report Parsing Issues**: A retry mechanism handles timing issues with report generation.

## Future Enhancements

Potential future improvements to the test execution feature include:

1. **Test History**: Store and display history of test runs for trend analysis.
2. **Scheduled Tests**: Allow users to schedule automatic test execution.
3. **Test Coverage Reports**: Add support for displaying test coverage metrics.
4. **Parallel Test Execution**: Implement parallel test execution across multiple services.
5. **Mock Mode**: Implement a mock mode for running tests when Docker is not available.

## Conclusion

The test execution feature significantly enhances the capabilities of the Poly Micro Manager, allowing users to validate their microservices without leaving the application. By leveraging Docker integration, the feature provides a seamless way to run tests in the same environment where services are deployed, ensuring accurate and reliable test results.
