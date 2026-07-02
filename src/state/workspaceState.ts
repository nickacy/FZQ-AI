import { create } from 'zustand';

type InputMode = 'free' | 'template';

interface SmartSuggestion {
  id: string;
  zh: string;
  en: string;
}

interface QuickTemplate {
  id: string;
  title: { zh: string; en: string };
  prompt: string;
}

interface WorkspaceState {
  // 输入区
  inputText: string;
  inputMode: InputMode;

  // 模板系统
  selectedTemplate: string | null;
  quickTemplates: QuickTemplate[];

  // 智能提示
  smartSuggestions: SmartSuggestion[];

  // 执行状态
  isRunning: boolean;

  // Actions
  setInputText: (text: string) => void;
  clearInput: () => void;

  setInputMode: (mode: InputMode) => void;

  setSelectedTemplate: (templateId: string | null) => void;
  setQuickTemplates: (templates: QuickTemplate[]) => void;

  setSmartSuggestions: (suggestions: SmartSuggestion[]) => void;

  setRunning: (status: boolean) => void;

  resetWorkspace: () => void;
}

export const useWorkspaceState = create<WorkspaceState>((set) => ({
  // 输入区
  inputText: '',
  inputMode: 'free',

  // 模板系统
  selectedTemplate: null,
  quickTemplates: [],

  // 智能提示
  smartSuggestions: [],

  // 执行状态
  isRunning: false,

  // Actions
  setInputText: (text) => set({ inputText: text }),
  clearInput: () => set({ inputText: '', selectedTemplate: null }),

  setInputMode: (mode) => set({ inputMode: mode }),

  setSelectedTemplate: (templateId) => set({ selectedTemplate: templateId }),
  setQuickTemplates: (templates) => set({ quickTemplates: templates }),

  setSmartSuggestions: (suggestions) => set({ smartSuggestions: suggestions }),

  setRunning: (status) => set({ isRunning: status }),

  resetWorkspace: () =>
    set({
      inputText: '',
      inputMode: 'free',
      selectedTemplate: null,
      smartSuggestions: [],
      isRunning: false,
    }),
}));
