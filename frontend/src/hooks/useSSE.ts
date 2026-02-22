export function useSSE() {
  return { responses: [], isRunning: false, isComplete: false, error: null, totalCompleted: 0 };
}
