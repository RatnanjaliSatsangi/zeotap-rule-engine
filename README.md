# Rule Engine with AST (Backend)

This is a Python-based backend for a rule engine that uses an Abstract Syntax Tree (AST) to define and evaluate rules. The backend supports concurrency and stores rules in an SQLite database.

## Features
- Create rules as ASTs and store them in SQLite.
- Combine rules into a single AST.
- Evaluate rules against provided data.
- Handle concurrent rule creation using Python threading.

## Setup

1. **Install dependencies:**
```pip install -r requirements.txt```

2. **Setup SQLite database:**
Run the following script to set up the database:
```python db_setup.py```

3. **Run the main application:**
```python main.py```

## Example Usage

1. **Creating rules:**
Rules can be created using the `create_rule()` function.

2. **Evaluating rules:**
Provide the rule ID and data dictionary to evaluate the rule.

3. **Concurrent rule creation:**
Multiple rules can be created concurrently using threads.

