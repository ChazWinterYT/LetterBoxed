// Utility to extract unique values
export const getUniqueValues = <T, K extends keyof T>(items: T[], key: K): T[K][] => {
  return Array.from(new Set(items.map((item) => item[key]))).filter((value): value is T[K] => !!value);
};

// Utility to generate ranges for filtering
export interface RangeOption {
  value: string;
  label: string;
}

export const generateRangeOptions = (key: string, ranges: RangeOption[]): { 
  propertyKey: string; value: string; label: string 
}[] => {
  return ranges.map((range) => ({
    propertyKey: key,
    value: range.value,
    label: range.label,
  }));
};

// Constants
// Batch size for fetching a list of games from the DB
export const FETCH_BATCH_SIZE = 80;
