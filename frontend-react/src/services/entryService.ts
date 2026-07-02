import { apiClient } from './apiClient';

import { useExecutionState } from '../state/executionState';
import { useOutputState } from '../state/outputState';
import { useWorkspaceState } from '../state/workspaceState';
import { useAgentState } from '../state/agentState';
import { useSystemState } from '../state/systemState';

export const entryService = {
  // --- 标准执行（非流式） ---
  async runEntry(text: string) {
    const { currentAgent } = useAgentState.getState();
    const { resetExecution, setUiSchema, syncExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    try {
      // 执行前清空旧状态
      resetExecution();
      resetOutputs();
      setRunning(true);

      const data = await apiClient.post('/entry', {
        text,
        agent: currentAgent,
      });

      syncExecution(data.execution);
      setUiSchema(data.ui_schema);

      setApiStatus('connected');
      setSystemHealth('healthy');
      setRunning(false);

      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      setRunning(false);
      throw err;
    }
  },

  // --- 多智能体执行 ---
  async runMulti(text: string, tasks: any[]) {
    const { resetExecution, setUiSchema, syncExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    try {
      resetExecution();
      resetOutputs();
      setRunning(true);

      const data = await apiClient.post('/multi', { text, tasks });

      syncExecution(data.execution);
      setUiSchema(data.ui_schema);

      setApiStatus('connected');
      setSystemHealth('healthy');
      setRunning(false);

      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      setRunning(false);
      throw err;
    }
  },

  // --- 自治智能体执行 ---
  async runAutonomy(text: string) {
    const { resetExecution, setUiSchema, syncExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    try {
      resetExecution();
      resetOutputs();
      setRunning(true);

      const data = await apiClient.post('/autonomy', { text });

      syncExecution(data.execution);
      setUiSchema(data.ui_schema);

      setApiStatus('connected');
      setSystemHealth('healthy');
      setRunning(false);

      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      setRunning(false);
      throw err;
    }
  },

  // --- 流式执行（SSE） ---
  async runEntryStream(text: string, onMessage: (msg: any) => void) {
    const { currentAgent } = useAgentState.getState();
    const { resetExecution, startStreaming, endStreaming } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();

    resetExecution();
    resetOutputs();
    setRunning(true);
    startStreaming();

    return apiClient.postStream(
      '/entry/stream',
      { text, agent: currentAgent },
      (msg) => {
        onMessage(msg);
        if (msg.type === 'result') {
          endStreaming();
          setRunning(false);
        }
      }
    );
  }
};
