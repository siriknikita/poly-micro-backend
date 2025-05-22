# Development Planning

## State 1

- [x] Initialize the FastAPI server
- [x] Learn the data structures of the application by looking at types, interfaces, mocked data, etc.
- [x] Replace the mocked data with the data from the FastAPI server endpoints
- [x] Implement grabbing the data on the Frontend
- [x] Test that everything works the same.

## State 2

- [x] Create a Database connection that will be used by the FastAPI server
- [x] Connect a database to the Backend
- [x] Test that we can query the database from the Backend

## State 3

- [x] Translate the TypeScript interfaces to the understandable pymongo schema (including the Pydantic model)
- [x] Make sure that all the models are implemented correctly and according to an existing structure.
- [x] Test that we can query the database from the Backend

## State 4

- [x] Implement basic CRUD operations for the models (Logs, Projects, Metrics, Users, Service, etc.)
    - [x] Implement the Creation operation
    - [x] Implement the Reading operation
    - [x] Implement the Updating operation
    - [x] Implement the Deleting operation
- [x] Test that we can query the database from the Backend

## State 5

- [x] Connect the Swagger to the Backend
- [x] Create a robust documentation for each of the endpoints
- [x] Test the queries from the Swagger UI

## State 6

- [x] Implement the in-memory testing database with the same structure as the production database
- [x] Test the implementation of the API using the Integration tests and Unit tests

## State 7

- [ ] Implement my own logger module, so that I can then parse the logs form the backend directly using the provided projectid in my database.
Note: We solve a problem of gathering the infromation about the microservices, projects, and other cool stuff, including the testing environment of the user for that specific project/microservice/etc.

Moreover, we will be able to parse in that way the output of the testing, so that it can be easily shown on the screen to the user when connected to the Frontned of an application.

- [ ] Using the prefix parsing, assign a new loogger instance to the project/microserivce/instance/etc.
- [ ] We can parse the CPU Usage/Memory Usage/Network Usage/Disk Usage directly form the docker-compose image.
- [ ] Store the obtained data somewhere on the local device storage (for the sake of simplicity)

## Stage 8

- [ ] Connect an AI model to the testing module, so that it can analyze the logs and provide insights, while also generating the additional tests.

### FOR THE FUTURE
- [ ] Implement the ability to run the local LLM/provide an API tokens directly from the settings page of an application.

## Stage 9

- [ ] Implement the CI/CD pipeline for the application
    - [ ] Use custom GitHub Actions events to trigger specific workflows.
    - [ ] Store the new custom github events templates.
    - [ ] Use the command line tools to trigger those workflows from the code based on a conditions specificied in a workflow itself
    - [ ] Send those events to the Github workflow automation pipelines defined by a user.
        - [ ] For each microservice, a user will be able to define the pipeline for that specific microservice.
        - [ ] We will create a wrapper around those pre-defined workflows, so that we can use them in the code.
        - [ ] We will parse the stdio output of the workflow, so that we can display it in the frontend & execute a specific actions based on a defined condition by a user/developer (me).
        - [ ] We will be able to emulate the workflow run itself by using a specific library for that case.
