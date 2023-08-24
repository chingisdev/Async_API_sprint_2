# Async API for Online Cinema
Asynchronous cinema API is designed to be the entry point for all clients interacting with online cinema services. Initially supporting only anonymous users, future iterations will include authorization and authentication functions through the Auth module.

### Technologies Used
- **Language**: Python + FastAPI
- **Server**: ASGI server (uvicorn)
- **Storage**: ElasticSearch
- **Caching**: Redis Cluster
- **Containerization**: Docker

## Installation and Usage
Follow these steps to install and run the project:

1. Clone the repository:
```shell
git clone https://github.com/credo7/Async_API_sprint_1.git
```
</br>

2. Set up the environment variables in an .env file in the root of the project:

| Variable            | Explanation                      | Example                  |
|---------------------|----------------------------------|--------------------------|
| `POSTGRES_HOST`     | PostgreSQL Hostname              | `postgres_test`          |
| `POSTGRES_PASSWORD` | PostgreSQL Password              | `123qwe`                 |
| `POSTGRES_USER`     | PostgreSQL User                  | `app`                    |
| `POSTGRES_DB`       | PostgreSQL Database Name         | `movies_database`        |
| `POSTGRES_PORT`     | PostgreSQL Port                  | `5432`                   |
| `REDIS_HOST`        | Redis Hostname                   | `redis_test`             |
| `REDIS_PORT`        | Redis Port                       | `6379`                   |
| `ELASTIC_HOST`      | ElasticSearch Hostname           | `elasticsearch_test`     |
| `ELASTIC_PORT`      | ElasticSearch Port               | `9200`                   |
| `ELASTIC_SCHEME`    | ElasticSearch Scheme (http/https)| `http`                   |
| `REPEAT_TIME_SECONDS`| Time Interval for Repeating Task| `15`                     |
</br>

3. make sure that every service in `docker-compose.yml` pointing to your env file:
```yaml
    env_file:
      - <your_path/.env>
```
4. Start the services:
```shell
docker-compose up
```
This command will:
- Start the containers
- Initialize the PostgreSQL database
- Fill the database with sample data
- Start the ETL process from PostgreSQL to ElasticSearch
- Start the movies API service

## Features
You can explore all the API endpoints through Swagger's interactive documentation. Once you have launched the application, simply copy and paste the following URL into your browser's address bar:

`http://localhost:8000/api/openapi`

This will provide you with detailed information about each endpoint, allowing you to understand and interact with the API more effectively.


## Contribution Guidelines

When contributing to this project, please follow these naming conventions for branches:

- **Valid Branch Actions (as action):** Use `feat` for features or `fix` for bug fixes.
- **Goal Action (as goal):** The goal must start with a verb and describe the branch's purpose.

### Valid Branch Name Example

Format: `issue_number/action-goal`

Example: `15/feat-add-sort-query-results`


## Setup Development Environment
1. You can prepare your local environment with this:
```shell
python -m venv venv &&
. venv/bin/activate &&
pip install -r requirements.txt &&
pre-commit install
```
