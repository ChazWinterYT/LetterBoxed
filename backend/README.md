# LetterBoxed Game Backend

This project is a backend implementation for a **LetterBoxed game** clone. It uses **AWS Lambda**, **DynamoDB**, and **API Gateway** for serverless functionality, and it is deployed using **AWS CDK**.

## Features

- Create custom game boards with solutions.
- Fetch pre-existing game boards by ID or standardized hash.
- Prefetch today's game data directly from the NYT Letter Boxed page.
- Supports different board sizes and multiple languages.

---

## Setup Instructions

### Python Virtual Environment

The project uses a virtual environment for Python dependencies.

To manually create and activate a virtual environment:

#### MacOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows:

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

Once activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

### AWS CDK Setup

The project uses **AWS CDK** for deploying infrastructure.

- **Install CDK CLI**:

  ```bash
  npm install -g aws-cdk
  ```

- **Bootstrap the Environment**:

  ```bash
  cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
  ```

- **Deploy the Stack**:
  ```bash
  cdk deploy
  ```

Use `cdk ls` to list all stacks and `cdk synth` to synthesize the CloudFormation template.

---

## Testing

The project uses **pytest** for testing. Mocking for DynamoDB and external services is handled with **pytest-mock**.

- **Run All Tests**:

  ```bash
  pytest
  pytest -v # Some verbose testing
  pytest -vv # More verbose testing
  ```

- **Key Test Files**:
  - `test_db_utils.py`: Tests for database interactions (add, fetch by ID, fetch by hash).
  - `test_prefetch_service.py`: Tests for the prefetch service functionality.

### Dependency: `pytest-mock`

If `pytest-mock` is not installed, add it to your virtual environment:

```bash
pip install pytest-mock
```

### Mocking DynamoDB

When testing with mocked DynamoDB tables, ensure the correct path is patched (e.g., `lambdas.common.db_utils.get_games_table`).

---

## Useful CDK Commands

- `cdk ls` - List all stacks in the app.
- `cdk synth` - Synthesize the CloudFormation template for this code.
- `cdk deploy` - Deploy the stack to your default AWS account/region.
- `cdk diff` - Compare the deployed stack with the current state.
- `cdk docs` - Open CDK documentation.

---

## Contributing

Feel free to submit issues and pull requests! For major changes, please open an issue first to discuss what you would like to change.

```

```
