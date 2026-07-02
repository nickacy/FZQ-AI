import { create } from 'zustand';
import { apiClient } from '../services/apiClient';

export interface Agent {
  id: string;
  name: { zh: string; en: string };
  description: { zh: string; en: string };
  capabilities: string[];
  avatar?: string;
  color?: string;
  category?: string;
  defaultPrompt?: string;
}

interface AgentState {
  agents: Agent[];
  currentAgent: string | null;

  isLoadingAgents: boolean;

  // Actions
  loadAgents: () => Promise<void>;
  setAgents: (agents: Agent[]) => void;

  selectAgent: (id: string) => void;
  clearSelection: () => void;

  setLoadingAgents: (status: boolean) => void;
}

export const useAgentState = create<AgentState>((set) => ({
  agents: [],
  currentAgent: null,

  isLoadingAgents: false,

  // 从后端加载智能体列表
  loadAgents: async () => {
    set({ isLoadingAgents: true });
    try {
      const data = await apiClient.post('/agents/list', {});
      set({ agents: data.agents || [] });
    } finally {
      set({ isLoadingAgents: false });
    }
  },

  setAgents: (agents) => set({ agents }),

  selectAgent: (id) => set({ currentAgent: id }),
  clearSelection: () => set({ currentAgent: null }),

  setLoadingAgents: (status) => set({ isLoadingAgents: status }),
}));
