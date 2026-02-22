export function useTestSession() {
  return { startTest: async (_desc: string) => {}, state: "idle" as const };
}
