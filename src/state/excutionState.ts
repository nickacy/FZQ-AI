import { create } from 'zustand';

type StateMachinePhase = 'DECOMPOSE' | 'ROUTE' | 'ACT' | 'REFLECT' | 'FINALIZE';

interface ExecutionState {
  // 数据
  timeline: any[];
  currentPhase: StateMachinePhase;
  traceId: string;
  uiSchema: any;
  
  // Actions
  syncExecution: (execution: any) => void;
  setUiSchema: (schema: any) => void;
}

export const useExecutionState = create<ExecutionState>((set) => ({
  timeline: [],
  currentPhase: 'DECOMPOSE',
  traceId: '',
  uiSchema: null,

  syncExecution: (execution) => {
    set({
      traceId: execution.trace_id,
      // 精准提取前端要求书第 7、8 节要求的数据
      timeline: execution.timeline || [],
      currentPhase: execution.state_machine?.current || 'FINALIZE',
    });
  },
  
  setUiSchema: (schema) => set({ uiSchema: schema }),
}));