const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitTest(description: string): Promise<{ test_id: string }> {
  const res = await fetch(`${BASE_URL}/api/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_description: description }),
  });
  return res.json();
}

export async function getResults(testId: string) {
  const res = await fetch(`${BASE_URL}/api/test/${testId}/results`);
  return res.json();
}

export async function getProfileStats() {
  const res = await fetch(`${BASE_URL}/api/profiles/stats`);
  return res.json();
}
