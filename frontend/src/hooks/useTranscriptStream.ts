import { useEffect } from 'react';

export function useTranscriptStream(onTranscript: (text: string) => void) {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/transcripts');
    ws.onmessage = (event) => onTranscript(event.data);
    return () => ws.close();
  }, [onTranscript]);
} 