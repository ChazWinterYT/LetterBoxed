# Letter Boxed Clone

A clone of the New York Times' **Letter Boxed** game, built as a web app to practice coding and using AWS resources. The game allows users to solve puzzles based on custom or generated letter configurations and provides solutions for equivalent boards by leveraging standardized hashing.

## Project Overview

This project is designed with:
- **Frontend**: A TypeScript-based React frontend for the game interface.
- **Backend**: Python-based Lambda functions for handling game logic, validation, and solution generation.
- **Database**: DynamoDB for storing unique game configurations and their solutions.

## Features

- **Create a Custom Game**: Users can input their own letters to create a new puzzle layout.
- **Fetch a Solution for Equivalent Games**: If an equivalent game configuration exists, the stored solution will be reused.
- **Standardized Layouts**: Each game layout is stored in DynamoDB, with solutions linked to a standardized hash for efficiency.

## Setup

### Prerequisites

- **Node.js** and **npm** for frontend development.
- **Python** and **pip** for backend development.
- **AWS CLI** and **AWS CDK** for infrastructure deployment.
- **AWS account** with IAM permissions to access DynamoDB and deploy Lambda functions.

### Project Installation

#### 1. Clone the Repository using any of the clone options available above.

#### 2. Install Dependencies

##### Backend (DynamoDB, Lambda)

Navigate to the backend directory, set up a virtual environment, and install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

##### Frontend (React)

Navigate to the frontend directory and install Node dependencies:

```bash
cd frontend
npm install
```

#### 3. Deploy the Backend with CDK

Ensure that the AWS CLI is configured with appropriate IAM permissions, then deploy the backend infrastructure:

```bash
cd backend
cdk bootstrap  # Run once to initialize resources
cdk deploy
```

### Development Notes

- **Unique and Standardized Game IDs**: Game entries are stored based on unique user layouts (`gameId`), while standardized layouts (`standardizedHash`) allow for equivalent games to share solutions.
- **Planned Features**: Implement random game generation with guaranteed solutions and enhanced board generation logic.

## Current Lambda Functions

- **validate_word**: Validates words within the game's constraints.
- **Standardized Solution Lookup**: Uses `standardizedHash` to fetch precomputed solutions for equivalent boards.

## Project Status

- **Current Progress**: Basic backend structure with DynamoDB setup and initial Lambda function for word validation.
- **Next Steps**: Implement additional Lambda functions for creating and retrieving games, and complete the frontend.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for any suggestions or questions.

