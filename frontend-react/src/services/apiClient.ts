import { useLanguageState } from '../state/languageState';
import { useSystemState } from '../state/systemState';

const BASE_URL = '/api/v1';

export const apiClient = {
  async post(endpoint: string, payload: any) {
    const { current } = useLanguageState.getState();
    const { setApiStatus, setBackendVersion, setHeartbeat } = useSystemState.getState();

    try {
      const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...payload, language: current }),
      });

      if (!response.ok) {
        setApiStatus('error');
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();

      // 更新系统状态
      setApiStatus('connected');
      if (data.backend_version) setBackendVersion(data.backend_version);
      setHeartbeat(Date.now());

      return data;
    } catch (err) {
      useSystemState.getState().setApiStatus('error');
      throw err;
    }
  },

  // SSE 流式执行（使用 fetch + ReadableStream）
  async postStream(endpoint: string, payload: any, onMessage: (msg: any) => void) {
    const { current } = useLanguageState.getState();
    const { setSseStatus } = useSystemState.getState();

    const url = `${BASE_URL}${endpoint}`;

    setSseStatus('streaming');

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({ ...payload, language: current }),
      });

      if (!response.body) {
        setSseStatus('error');
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setSseStatus('idle');
              return;
            }
            try {
              const parsed = JSON.parse(data);
              onMessage(parsed);
            } catch {
              console.warn('Invalid SSE message:', data);
            }
          }
        }
      }

      setSseStatus('idle');
    } catch (err) {
      setSseStatus('error');
      throw err;
    }
  }
};
