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

  // SSE 流式执行
  async postStream(endpoint: string, payload: any, onMessage: (msg: any) => void) {
    const { current } = useLanguageState.getState();
    const { setSseStatus } = useSystemState.getState();

    const url = `${BASE_URL}${endpoint}`;

    setSseStatus('streaming');

    const eventSource = new EventSource(url, {
      withCredentials: false,
    });

    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        setSseStatus('idle');
        eventSource.close();
        return;
      }

      try {
        const parsed = JSON.parse(event.data);
        onMessage(parsed);
      } catch {
        console.warn('Invalid SSE message:', event.data);
      }
    };

    eventSource.onerror = () => {
      setSseStatus('error');
      eventSource.close();
    };

    return eventSource;
  }
};
