import { useEffect, useState } from 'react';

export function useProcessingStatus() {
  const [status, setStatus] = useState<'idle' | 'processing'>('idle');
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/status');
    ws.onmessage = (event) => setStatus(event.data as 'idle' | 'processing');
    return () => ws.close();
  }, []);
  return status;
} 