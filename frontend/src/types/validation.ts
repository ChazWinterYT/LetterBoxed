export interface ValidationResult {
    valid: boolean;
    message: string;
    submittedWord: string;
    originalWord: string;
    gameCompleted: boolean;
    officialSolution: string[]; // Array of strings
    someOneWordSolutions: string[]; // Array of strings
    someTwoWordSolutions: [string, string][]; // Array of tuples (string, string)
    numOneWordSolutions: number;
    numTwoWordSolutions: number;
  }