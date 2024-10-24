# Rule Engine Application

## Overview

This is a **Rule Engine** application that allows users to create, combine, and evaluate rules dynamically. The application is built using Python with Flask for the web server and SQLite as the database to store the rules.

Users can:
1. Create new rules with custom logic.
2. Combine existing rules.
3. Evaluate rules by inputting values for the variables in the rules.

The UI dynamically adapts to show existing rules, combines rules, and evaluates rules with a clear success or failure response.

---

## Features

- **Create Rules**: Define rules with conditions that are stored in the SQLite database.
- **Combine Rules**: Combine multiple rules to create a complex logic rule.
- **Evaluate Rules**: Input values for the variables and evaluate if the rule passes or fails.
- **UI**: Simple, user-friendly interface built using HTML, CSS, and JavaScript to dynamically fetch and display rules and results.

---

## Dependencies

1. **Python 3.9+**
2. **Flask** - Web framework to build the API and serve the web pages.
3. **SQLite** - Lightweight database to store rules and their metadata.
4. **Docker** - To containerize the application for easy deployment (Optional).
5. **Flask-CORS** (Optional, but useful for allowing cross-origin requests).

### Python Packages

These packages can be installed via `pip`:

```bash
pip install Flask
pip install sqlite3
```

### Docker

To containerize the app, you'll need:
- **Docker** (install from [Docker's official site](https://docs.docker.com/get-docker/))
- **Docker Compose** (optional but useful for managing multi-container Docker applications)

---

## Build Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd rule-engine-app
```

### 2. Setup Python Environment

Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows, use venv\Scripts\activate
```

Install the necessary dependencies:

```bash
pip install Flask
```

### 3. Initialize the SQLite Database

To create the `rules.db` database, run the `db_setup.py` script:

```bash
python db_setup.py
```

This script will create a new SQLite database and the necessary `rules` table.

### 4. Run the Flask Application

Start the Flask server by running the following command:

```bash
export FLASK_APP=main.py
export FLASK_ENV=development  # Optional: for debugging mode
flask run
```

Alternatively, you can use:

```bash
python main.py
```

The application will be available at: `http://127.0.0.1:5000/`.

---

## Docker Instructions (Optional)

If you want to run the application inside a Docker container:

### 1. Create a `Dockerfile`

Create a `Dockerfile` in the root directory:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
```

### 2. Create a `docker-compose.yml` (Optional)

To simplify running the app and its services (like the database), you can use `docker-compose.yml`:

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    command: flask run --host=0.0.0.0
```

### 3. Build and Run the Docker Container

Run the following command to build and run the Docker container:

```bash
docker-compose up --build
```

This will build the image and run the Flask app in a container. The application will be available at `http://localhost:5000/`.

---

## Project Structure

```bash
rule-engine-app/
│
├── static/
│   └── styles.css             # Styles for the frontend
│
├── templates/
│   └── index.html             # Main HTML file for the frontend
│
├── db_setup.py                # Script to initialize the SQLite database
├── main.py                    # Flask entry point for the application
├── rule_engine.py             # Backend logic for handling rules, combining, evaluating
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Dockerfile for containerization (Optional)
├── docker-compose.yml         # Docker-compose file (Optional)
└── README.md                  # This README file
```

---

## Design Choices

1. **SQLite**: Chosen for its simplicity and lightweight nature, perfect for small-scale applications or testing.
2. **Flask**: Lightweight Python web framework, easy to integrate with SQLite and build REST APIs.
3. **Separation of Concerns**: 
   - `rule_engine.py` handles all business logic (rule parsing, combining, evaluation).
   - `main.py` focuses on API and routing logic.
4. **Frontend with Vanilla JS**: Basic JavaScript is used for fetching and dynamically displaying rules and evaluation results.
5. **Docker**: To ensure easy containerization and deployment, Docker and Docker Compose files have been included. This allows the application to be packaged and run in any environment with minimal setup.
6. **Dynamic Rule Evaluation**: The design leverages the dynamic construction and evaluation of rules. User inputs are inserted into rule templates, and the logic is evaluated using Python's `eval()` function, allowing for flexible and complex rule combinations.

---

## Usage

1. **Create Rule**: Enter a rule name and the rule definition using operators like `AND`, `OR`, `>`, `<`, etc. Example rule:
   ```
   (age > 30 AND salary > 50000) OR (experience > 5)
   ```
2. **Combine Rules**: Enter multiple rule IDs to combine them using logical connectors like `AND` or `OR`.
3. **Evaluate Rule**: Select a rule, provide values for variables (e.g., `age`, `salary`, `experience`), and check whether the rule passes.

### Example Rule:

```plaintext
((age > 30 AND department = 'Sales') OR (salary > 50000)) AND (experience > 5)
```

To evaluate this, the user would provide values for `age`, `department`, `salary`, and `experience`.

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it as needed.

---

## Contributing

If you'd like to contribute, feel free to submit issues or pull requests. Please make sure to update tests as appropriate and adhere to the existing coding style.

---

This README covers everything from installation, building, and running the application to design considerations and usage instructions.