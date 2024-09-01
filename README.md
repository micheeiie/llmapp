# Govtech Intern Assignment

## Getting Started

Before you begin, ensure you have the following installed:

- **Docker:** [Installation guide](https://docs.docker.com/get-docker/)
- **Docker Compose:** [Installation guide](https://docs.docker.com/compose/install/)


Follow these steps to get the  application up and running.

### 1. Clone the Repository

```bash
git clone https://github.com/micheeiie/llmapp
cd llmap
```

### 2. Build and Run the Application

```bash
docker-compose up --build
```

### 3. Access the endpoints

Visit [http://localhost:8000/](http://localhost:8000/) to access the endpoints

## Backend Application Design

The backend application contains 4 main files:
1. `main.py`: Entry point to the application. Contains endpoint and route definitions
2. `database.py`: Contains functions to connect the application to the mongodb instance 
3. `schemas.py`: Contains document definitions and data transfer objects
4. `utils.py`: Contains helper functions for working with OpenAI API
