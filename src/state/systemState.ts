import { create } from 'zustand';

type ApiStatus = 'connected' | 'disconnected' | 'error';
type SystemHealth = 'healthy' | 'degraded' | 'down';
type SseStatus = 'idle' | 'streaming' | 'error';

interface FeatureFlags {
  enableSSE: boolean;
  enableMultiAgent: boolean;
  enableAdvancedSchema: boolean;
  enableDynamicTheme: boolean;
}

interface SystemState {
  apiStatus: ApiStatus;
  systemHealth: SystemHealth;

  systemVersion: string;
  backendVersion: string;

  lastHeartbeat: number;

  sseStatus: SseStatus;

  featureFlags: FeatureFlags;

  // Actions
  setApiStatus: (status: ApiStatus) => void;
  setSystemHealth: (health: SystemHealth) => void;

  setBackendVersion: (version: string) => void;
  setHeartbeat: (timestamp: number) => void;

  setSseStatus: (status: SseStatus) => void;

  setFeatureFlags: (flags: Partial<FeatureFlags>) => void;

  resetSystem: () => void;
}

export const useSystemState = create<SystemState>((set) => ({
  apiStatus: 'disconnected',
  systemHealth: 'healthy',

  systemVersion: '24.0.0',
  backendVersion: '',

  lastHeartbeat: Date.now(),

  sseStatus: 'idle',

  featureFlags: {
    enableSSE: true,
    enableMultiAgent: true,
    enableAdvancedSchema: true,
    enableDynamicTheme: true,
  },

  setApiStatus: (status) => set({ apiStatus: status }),
  setSystemHealth: (health) => set({ systemHealth: health }),

  setBackendVersion: (version) => set({ backendVersion: version }),
  setHeartbeat: (timestamp) => set({ lastHeartbeat: timestamp }),

  setSseStatus: (status) => set({ sseStatus: status }),

  setFeatureFlags: (flags) =>
    set((state) => ({
      featureFlags: { ...state.featureFlags, ...flags },
    })),

  resetSystem: () =>
    set({
      apiStatus: 'disconnected',
      systemHealth: 'healthy',
      backendVersion: '',
      lastHeartbeat: Date.now(),
      sseStatus: 'idle',
      featureFlags: {
        enableSSE: true,
        enableMultiAgent: true,
        enableAdvancedSchema: true,
        enableDynamicTheme: true,
      },
    }),
}));
