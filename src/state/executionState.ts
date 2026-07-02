import { create } from 'zustand';

type Phase = 'DECOMPOSE' | 'ROUTE' | 'ACT' | 'REFLECT' | 'FINALIZE';

interface TimelineEvent {
  agent: string;
  step: string;
  input: string;
  output: string;
  timestamp: string;
}

interface ExecutionData {
  intent: Record<string, any>;
  route: Record<string, any>;
  pipeline: Record<string, any>;
  model: Record<string, any>;
  agent: Record<string, any>;
  state_machine: {
    current: Phase;
    history: Phase[];
  };
  timeline: TimelineEvent[];
  duration_ms: number;
  trace_id: string;
}

interface ExecutionState {
  // 原始执行数据
  executionRaw: ExecutionData | null;

  // 状态机
  currentPhase: Phase;
  stateHistory: Phase[];

  // timeline
  timeline: TimelineEvent[];

  // 执行耗时
  durationMs: number;

  // 智能体名称
  agentName: string | null;

  // UI Schema
  uiSchema: Record<string, any> | null;

  // 流式执行支持
  isStreaming: boolean;
  streamBuffer: TimelineEvent[];

  // Actions
  syncExecution: (execution: ExecutionData) => void;
  setUiSchema: (schema: Record<string, any> | null) => void;

  startStreaming: () => void;
  pushStreamEvent: (event: TimelineEvent) => void;
  endStreaming: () => void;

  resetExecution: () => void;
}

export const useExecutionState = create<ExecutionState>((set) => ({
  executionRaw: null,

  currentPhase: 'DECOMPOSE',
  stateHistory: [],

  timeline: [],
  durationMs: 0,

  agentName: null,

  uiSchema: null,

  isStreaming: false,
  streamBuffer: [],

  syncExecution: (execution) => {
    set({
      executionRaw: execution,
      traceId: execution.trace_id,

      currentPhase: execution.state_machine?.current || 'FINALIZE',
      stateHistory: execution.state_machine?.history || [],

      timeline: execution.timeline || [],
      durationMs: execution.duration_ms || 0,

      agentName: execution.agent?.name || null,
    });
  },

  setUiSchema: (schema) => set({ uiSchema: schema }),

  startStreaming: () => set({ isStreaming: true, streamBuffer: [] }),

  pushStreamEvent: (event) =>
    set((state) => ({
      streamBuffer: [...state.streamBuffer, event],
    })),

  endStreaming: () =>
    set((state) => ({
      isStreaming: false,
      timeline: [...state.timeline, ...state.streamBuffer],
      streamBuffer: [],
    })),

  resetExecution: () =>
    set({
      executionRaw: null,
      currentPhase: 'DECOMPOSE',
      stateHistory: [],
      timeline: [],
      durationMs: 0,
      agentName: null,
      uiSchema: null,
      isStreaming: false,
      streamBuffer: [],
    }),
}));
