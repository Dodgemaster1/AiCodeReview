# AiCodeReview

## Description
This tool with simple frontend component can help automate the process of reviewing coding assignments 
by leveraging GoogleAI API for code analysis and the GitHub API for repository access

## Features
- Interact with the GoogleAI API to analyze code
- Interact with the GitHub API to access repositories
- Connect to a Redis for caching LLM responses

## Requirements
- Python 3.10+ (tested on Python 3.12.8)

## Installation

### Using pip
1. Clone the repository:
    ```sh
    git clone https://github.com/Dodgemaster1/AiCodeReview.git
    cd AiCodeReview
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Using Poetry
1. Clone the repository:
    ```sh
    git clone https://github.com/Dodgemaster1/AiCodeReview.git
    cd AiCodeReview
    ```

2. Install Poetry if you haven't already:
    ```sh
    pip install poetry
    ```

3. Install the dependencies:
    ```sh
    poetry install --no-root --no-dev
    ```

4. Activate the virtual environment:
    ```sh
    poetry shell
    ```

### Using Docker
1. Clone the repository:
    ```sh
    git clone https://github.com/Dodgemaster1/AiCodeReview.git
    cd AiCodeReview
    ```

## Configuration
1. Rename the `config_example.json` to `config.json`:
    ```sh
    mv config_example.json config.json
    ```

2. Edit the `config.json` file to include your API keys and Redis configuration

## Running the Application
### Without Docker:
Run the application:
```sh
uvicorn src.main:app --host 0.0.0.0 --port 80
```
### Using Docker:
Run the application:
```sh
docker-compose up --build
```

## Usage
Go to http://127.0.0.1 in browser or send a POST request to `http://localhost:80/review` with the following JSON body:
```json
{
    "assignment_description": "assignment description text",
    "github_repo_url": "https://github.com/your_name/your_repository_name",
    "candidate_level": "Junior/Middle/Senior"
}
```
Example:
```json
{
    "assignment_description": "Create asynchronous TCP server",
    "github_repo_url": "https://github.com/Dodgemaster1/AsyncTCPServer",
    "candidate_level": "Junior"
}
```
Response structure:
```json
{
    "found_files": "README.md, src/app/__init__.py, src/app/client.py, ...",
    "comments": "The project demonstrates a good understanding of asynchronous programming in Python using asyncio...",
    "rating": "9",
    "conclusion": "The candidate demonstrates a solid understanding of asynchronous programming..."

}
```

## Testing
Run the tests using the following command (to run you should install dev dependencies via poetry):
   ```sh
   pytest -v
   ```

## Project Structure
```
.
├── .gitignore
├── README.md
├── config.json
├── config_example.json
├── requirements.txt
├── pyproject.toml
├── pypoetry.lock
├── Dockerfile
├── docker-compose.yml
└── src
    ├── __init__.py
    ├── main.py
    ├── models.py
    ├── utils
    │   ├── __init__.py
    │   ├── ai_api.py
    │   ├── github_api.py
    │   ├── redis.py
    │   └── read_config.py
    ├── static
    │   ├── styles.css
    │   └── favicon.svg
    └── templates
        ├── index.html
        └── review.html
```


## Scaling Strategy

1. **Load Balancing**:
   - Use a load balancer (e.g., AWS ELB, NGINX) to distribute incoming requests across multiple instances of the backend service. This ensures that no single instance is overwhelmed by the traffic.

2. **Horizontal Scaling**:
   - Deploy multiple instances of the backend service to handle increased traffic. Use container orchestration tools like Kubernetes to manage and scale these instances dynamically based on the load.

3. **Task Queues**:
   - Use task queues (e.g., Celery with Redis or RabbitMQ) to handle long-running tasks such as fetching repository contents and analyzing code. This allows the service to process requests in the background and return responses quickly.

4. **Database Optimization**:
   - Use a scalable database solution (e.g., AWS RDS, MongoDB Atlas) to store review results and other persistent data. Ensure the database is optimized for read and write operations to handle high traffic.

5. **Rate Limiting and Backoff Strategies**:
   - Implement rate limiting to control the number of requests to the GitHub and OpenAI APIs. Use exponential backoff strategies to handle rate limit errors and retry requests after a delay.

6. **API Gateway**:
   - Use an API Gateway (e.g., AWS API Gateway) to manage and throttle incoming requests. This helps in controlling the traffic and ensuring that the backend service is not overwhelmed.

7. **Monitoring and Logging**:
   - Implement comprehensive monitoring and logging (e.g., using Prometheus, Grafana, ELK stack) to track the performance and health of the service. This helps in identifying and resolving issues quickly.

8. **Cost Management**:
   - Monitor the usage of the OpenAI and GitHub APIs to manage costs effectively. Consider using alternative APIs or optimizing the prompts to reduce the number of tokens used in each request.
