# picodi-fastapi-example

[![Build Status](https://github.com/yakimka/picodi-fastapi-example/actions/workflows/workflow-ci.yml/badge.svg?branch=main&event=push)](https://github.com/yakimka/picodi-fastapi-example/actions/workflows/workflow-ci.yml)
[![Codecov](https://codecov.io/gh/yakimka/picodi-fastapi-example/branch/main/graph/badge.svg)](https://codecov.io/gh/yakimka/picodi-fastapi-example)

Example FastAPI project with [Picodi](https://github.com/yakimka/picodi) integration.

Picodi is a Python DI inspired by FastAPI’s dependency injection system,
but it’s a standalone library that can be used in any Python application.

## About the project

This project is an example of how to use Picodi with FastAPI.
Although the project is the FastAPI example, you can use Picodi in any Python application.

This is example of simple weather API with user authentication.
Please note that this project is not example of best practices in FastAPI development,
but rather an example of how to use Picodi with FastAPI.

## How to run the project

### Local installation

1. Clone this repository:
2. Install dependencies with poetry:
   ```bash
   poetry install
   ```
3. Run the project with poetry:
   ```bash
   poetry run uvicorn --factory app.api.main:create_app --host=0.0.0.0 --port=8000
   ```
4. Open the browser and go to [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker

1. Spin up the container:
    ```bash
    docker run --rm -p 8000:8000 yakimka/picodi-fastapi-example:latest
    ```
2. Open the browser and go to [http://localhost:8000/docs](http://localhost:8000/docs)

## How to read the code

The project is divided into several parts:

1. `picodi_app` - the main package of the project.
2. `picodi_app.conf` - application configuration.
3. `picodi_app.cli` - the CLI commands.
4. `picodi_app.workers` - the background workers.
5. `picodi_app.deps` - Picodi dependencies.
   DB connections, http clients, all dependencies
   that can be used not only in HTTP-related code but in any part of the application
   like CLI commands or background workers.
6. `picodi_app.api` - the FastAPI application. All FastAPI-related code is here.
7. `picodi_app.api.fastapi-deps` - FastAPI dependencies. This is FastAPI\HTTP related dependencies.
8. `picodi_app.data_access` - the data access layer.
   All interactions with the database and external services are here.
9. `picodi_app.user`, `picodi_app.weather` - "business logic" modules.
   Usually this code is in the `domain` package,
   but I decided to put it in the root package for simplicity.

You can read all code file by file,
or you can cherry-pick some parts of the code related to Picodi integration.
This parts of code are marked with comments like `# Picodi Note:`.

## How to run tests

1. Run redis server:
   ```bash
   docker compose up -d redis
   ```
2. Run tests:
    ```bash
    make test
    ```

## License

[MIT](https://github.com/yakimka/picodi-fastapi-example/blob/main/LICENSE)


## Credits

This project was generated with [`yakimka/cookiecutter-pyproject`](https://github.com/yakimka/cookiecutter-pyproject).
