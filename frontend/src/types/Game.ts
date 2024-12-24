export interface Game {
    gameId: string;
    gameLayout: string;
    gameType: string;
    language: string;
    boardSize: string;
    createdAt: string;
    createdBy: string;
    hint: string;
    validWordCount: number;
    oneWordSolutionCount: number;
    twoWordSolutionCount: number;
    totalRatings: number;
    averageRating: number;
    totalCompletions: number;
    averageWordsNeeded: number;
}