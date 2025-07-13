// Voice API functions
export const startListener = async () => {
  await fetch('/voice/start', { method: 'POST' });
};

export const stopListener = async () => {
  await fetch('/voice/stop', { method: 'POST' });
};

export const uploadAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/voice/upload', { method: 'POST', body: formData });
  return res.json(); // { transcript, result }
}; 