# Letter Boxed Clone

A clone of The New York Times' **Letter Boxed** game, built as a web app to practice coding, algorithm design, and AWS resources. The game supports custom puzzles, random board generation, and solution generation for user-created games, leveraging AWS Lambda, S3, and DynamoDB.

## Project Overview

### Technologies Used

- **Frontend**: React (v17+), TypeScript (v4+)
- **Backend**: Python 3.10+, AWS Lambda, AWS CDK
- **Database**: AWS DynamoDB
- **Cloud Storage**: AWS S3
- **Other Tools**: AWS API Gateway, AWS IAM, Pytest (for testing)

### Features

- **Play Today's Game**: Fetch and play the daily Letter Boxed puzzle from the NYT website.
- **Custom Games**: Create and solve custom puzzles with user-defined configurations.
- **Archive Access**: Access and play any past NYT Letter Boxed puzzle.
- **Random Games**: Generate random puzzles guaranteed to have at least one solution.
- **Solutions Generator**: Automatically calculate and display two-word and three-word solutions.
- **Multi-language Support**: Supports dictionaries in multiple languages (e.g., English, Spanish).
- **Standardized Board Layouts**: Reuse solutions for equivalent boards using standardized hashing.
- **Responsive Design**: Optimized for both desktop and mobile browsers.

---

## Setup

### Prerequisites

Ensure you have the following installed:

- **Node.js** v14.x or newer and **npm**
- **Python** 3.8 or newer
- **AWS CLI** configured with your AWS credentials
- **AWS CDK** v2.x (`npm install -g aws-cdk`)
- **An AWS Account** with permissions to access DynamoDB, S3, Lambda, and API Gateway

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/ChazWinterYT/LetterBoxed.git
cd LetterBoxed
```

#### 2. Environment Variables

- **Backend `.env` File**:

  Create a `.env` file in the `backend/` directory:

  ```plaintext
  DICTIONARY_SOURCE=local
  S3_BUCKET_NAME=your-s3-bucket-name
  DICTIONARY_BASE_PATH=LetterBoxed/Dictionaries/
  DEFAULT_LANGUAGE=en
  ```

  Replace `your-s3-bucket-name` with the name of your S3 bucket.

#### 3. Install Dependencies

##### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

##### Frontend

```bash
cd frontend
npm install
```

#### 4. Deploy the Backend and Upload Dictionaries

First, ensure your AWS credentials are configured.

Then, make the upload script executable:

```bash
cd backend
chmod +x upload_dictionaries.py
```

Deploy the backend and upload dictionaries:

```bash
./deploy_with_upload.sh
```

This script will:

- Deploy the AWS CDK stack, creating necessary AWS resources.
- Upload the dictionaries to your specified S3 bucket.

#### 5. Start the Frontend

```bash
cd frontend
npm start
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the app.

---

## Lambda Functions

### Overview

The backend uses AWS Lambda functions for handling game logic and API endpoints:

- **`fetch_game`**: Retrieves a game by its ID.
- **`play_today`**: Retrieves the daily NYT game or falls back to the previous day's puzzle.
- **`create_custom`**: Creates custom games and generates solutions.
- **`prefetch_todays_game`**: Scheduled to preload the NYT daily puzzle into DynamoDB.
- **`validate_word`**: Validates user-submitted words against game rules.
- **`game_archive`**: Provides a list of available NYT games in the archive.

### Permissions

Each Lambda function requires specific permissions:

- **DynamoDB Access**: Read and write permissions for the `GAME_TABLE` and `VALID_WORDS_TABLE`.
- **S3 Access**: Read permissions for dictionaries in `DICTIONARY_PATH`.
- **AWS IAM Roles**: Defined in the AWS CDK stack with least privilege access.

---

## Development Notes

### Key Concepts

- **Standardized Hashing**: Boards are hashed based on their standardized layout to identify and reuse equivalent solutions.
- **Word Validation Rules**:
  - Words must alternate sides of the puzzle.
  - Letters within a side must be used sequentially.
  - All letters in the puzzle must be used at least once to solve the game.
- **Multi-language Support**: The app can support additional languages by adding corresponding dictionaries to the S3 bucket.

### Testing

Tests are written using `pytest`. To run tests:

```bash
cd backend
pip install -r requirements-dev.txt  # Install testing dependencies
pytest -vv
```

### Planned Enhancements

- **User Authentication**: Implement login functionality to save progress and track scores.
- **Enhanced Random Generation**: Improve algorithms for generating more diverse and challenging random puzzles.
- **Additional Languages**: Add support for more languages (e.g., French, German).
- **Hints System**: Provide optional hints to assist players.

---

## Contributing

Contributions are welcome!

- **Fork the Repository**: Make your changes in a new branch.
- **Coding Standards**: Follow PEP 8 for Python and standard conventions for JavaScript/TypeScript.
- **Commit Messages**: Write clear and descriptive commit messages.
- **Pull Requests**: Submit a pull request with a detailed description of your changes.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

### **Thank you for your interest in the Letter Boxed Clone project!**

---
