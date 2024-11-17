# Letter Boxed Clone

A clone of the New York Times' **Letter Boxed** game, built as a web app to practice coding, algorithm design, and AWS resources. The game supports custom puzzles, random board generation, and solution generation for user-created games, leveraging AWS Lambda, S3, and DynamoDB.

## Project Overview

### Technologies Used
- **Frontend**: A React-based interface written in TypeScript.
- **Backend**: Python-based Lambda functions for game logic, validation, and solution generation.
- **Database**: DynamoDB for storing game configurations, solutions, and standardized board hashes.
- **Cloud Storage**: AWS S3 for managing word dictionaries.

### Features
- **Play Today's Game**: Fetch the daily Letter Boxed puzzle from the NYT website, automatically preloaded.
- **Custom Games**: Create puzzles with custom configurations.
- **Archive of NYT Games**: Access any past NYT Letter Boxed puzzle.
- **Random Games**: Generate random puzzles with guaranteed solutions.
- **Solutions**: Automatically calculate and fetch two-word and three-word solutions.
- **Multi-language Support**: Supports dictionaries in multiple languages.
- **Standardized Board Layouts**: Boards are stored in DynamoDB with standardized hashing to reuse equivalent solutions.

---

## Setup

### Prerequisites
Ensure you have the following installed:
- **Node.js** and **npm** for frontend development.
- **Python** and **pip** for backend development.
- **AWS CLI** and **AWS CDK** for deployment.
- **AWS Account** with permissions to access DynamoDB, S3, and deploy Lambda functions.

---

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/your-repo.git
cd LetterBoxed
```

#### 2. Environment Variables
- **Backend `.env` File**:
  Create a `.env` file in the `backend/` folder:
  ```plaintext
  DICTIONARY_SOURCE=local
  S3_BUCKET_NAME=chazwinter.com
  DICTIONARY_BASE_PATH=LetterBoxed/Dictionaries/
  DEFAULT_LANGUAGE=en
  ```

#### 3. Install Dependencies

##### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

##### Frontend
```bash
cd frontend
npm install
```

#### 4. Upload Dictionaries to S3
To upload dictionaries:
```bash
cd backend
python upload_dictionaries.py
```

Ensure your dictionaries are in a `dictionaries/` directory in the project root, organized by language (e.g., `dictionaries/en/words.txt`).

#### 5. Deploy the Backend
```bash
cd backend
cdk bootstrap  # Run once for setup
cdk deploy
```

#### 6. Start the Frontend
```bash
cd frontend
npm start
```

---

## Lambda Functions

### Overview
The backend uses AWS Lambda functions for handling various game logic tasks:

- **`fetch_game`**: Fetches a game by ID.
- **`play_today`**: Fetches the daily NYT game or falls back to the previous day during the update gap.
- **`create_custom`**: Creates and stores custom games with generated solutions.
- **`prefetch_todays_game`**: Preloads the NYT daily puzzle into DynamoDB.
- **`validate_word`**: Validates words against game constraints and board rules.
- **`game_archive`**: Fetches a list of NYT games available in the archive.

### Permissions
Each Lambda function:
- **Reads and Writes** to DynamoDB (`GAME_TABLE`).
- **Reads** dictionaries stored in S3 (`DICTIONARY_PATH`).

---

## Development Notes

### Key Concepts
- **Standardized Layouts**: Boards are stored in DynamoDB with standardized hashes (`standardizedHash`) for efficient solution reuse.
- **Word Validation**: Implements strict rules to ensure solutions alternate puzzle sides and use all available letters.
- **Multi-language Support**: Dynamically loads language-specific dictionaries from S3.

### Testing
Tests use `pytest` and `pytest-mock` to validate logic and ensure robustness:
```bash
pytest --cov=lambdas
```

### Planned Enhancements
- Enhanced random board generation.
- User authentication for saving progress.
- Improved multilingual support with additional dictionaries.

---

## Contributing

Contributions are welcome! Submit pull requests or open issues for suggestions or bugs.

---

