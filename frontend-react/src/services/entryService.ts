/**
 * entryService.ts — V24-Final
 * Unified API client: single / multi / autonomy + streaming
 * All responses conform to V24Response contract.
 */
import { apiClient } from './apiClient';
import { schemaAdapter } from './schemaAdapter';
import type { V24Response, OutputCard } from './types';

import { useExecutionState } from '../state/executionState';
import { useOutputState } from '../state/outputState';
import { useWorkspaceState } from '../state/workspaceState';
import { useAgentState } from '../state/agentState';
import { useSystemState } from '../state/systemState';

// ── Helper ───────────────────────────────────────────────────

function processResponse(data: V24Response): OutputCard[] {
  const cards = schemaAdapter(data.ui_schema);
  const { syncExecution, setUiSchema } = useExecutionState.getState();
  const { setCards } = useOutputState.getState();
  syncExecution(data.execution as any);
  setUiSchema(data.ui_schema);
  setCards(cards as any);
  return cards;
}

// ── Entry Service ────────────────────────────────────────────

export const entryService = {

  async runEntry(text: string): Promise<V24Response> {
    const { currentAgent } = useAgentState.getState();
    const { resetExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    resetExecution();
    resetOutputs();
    setRunning(true);

    try {
      const data: V24Response = await apiClient.post('/entry', {
        input: text,
        agent: currentAgent,
      });
      processResponse(data);
      setApiStatus('connected');
      setSystemHealth('healthy');
      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      throw err;
    } finally {
      setRunning(false);
    }
  },

  async runMulti(text: string, tasks: any[]): Promise<V24Response> {
    const { resetExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    resetExecution();
    resetOutputs();
    setRunning(true);

    try {
      const data: V24Response = await apiClient.post('/multi', {
        input: text,
        tasks,
      });
      processResponse(data);
      setApiStatus('connected');
      setSystemHealth('healthy');
      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      throw err;
    } finally {
      setRunning(false);
    }
  },

  async runAutonomy(text: string): Promise<V24Response> {
    const { resetExecution } = useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();
    const { setApiStatus, setSystemHealth } = useSystemState.getState();

    resetExecution();
    resetOutputs();
    setRunning(true);

    try {
      const data: V24Response = await apiClient.post('/autonomy', {
        input: text,
      });
      processResponse(data);
      setApiStatus('connected');
      setSystemHealth('healthy');
      return data;
    } catch (err) {
      setApiStatus('error');
      setSystemHealth('degraded');
      throw err;
    } finally {
      setRunning(false);
    }
  },

  async runEntryStream(
    text: string,
    onMessage: (msg: any) => void
  ): Promise<void> {
    const { currentAgent } = useAgentState.getState();
    const { resetExecution, startStreaming, endStreaming } =
      useExecutionState.getState();
    const { resetOutputs } = useOutputState.getState();
    const { setRunning } = useWorkspaceState.getState();

    resetExecution();
    resetOutputs();
    setRunning(true);
    startStreaming();

    return apiClient.postStream(
      '/entry/stream',
      { text, agent: currentAgent },
      (msg: any) => {
        onMessage(msg);
        if (msg.type === 'result') {
          endStreaming();
          setRunning(false);
        }
      }
    );
  },
};
