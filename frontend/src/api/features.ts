// Features API functions
export const setMoodIntent = async (enabled: boolean) => {
  await fetch('/features/mood_intent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled }),
  });
}; 