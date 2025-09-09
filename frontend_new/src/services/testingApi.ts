export type RedTeamItem = {
  category: string;
  source_question: string;
  generated_question: string;
};

export async function loadRedTeamSet(): Promise<RedTeamItem[]> {
  const res = await fetch('/testing/redteam_questions.json');
  if (!res.ok) throw new Error('Failed to load redteam questions');
  const data = await res.json();
  return data.items as RedTeamItem[];
}

export type ChatResponse = { reply: string };

export async function askBackend(message: string): Promise<ChatResponse> {
  // Reuse existing proxy to backend
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`Backend error ${res.status}`);
  return res.json();
}
