import { create } from 'zustand';

interface GlobalState {
  // App lifecycle
  isAppReady: boolean;
  setAppReady: (status: boolean) => void;

  // Global loading indicator
  isGlobalLoading: boolean;
  setGlobalLoading: (status: boolean) => void;

  // Global error handler
  globalError: string | null;
  setGlobalError: (error: string | null) => void;

  // UI layout
  isSidebarOpen: boolean;
  toggleSidebar: () => void;

  // Session & version
  sessionId: string;
  appVersion: string;

  // Network status
  networkStatus: 'online' | 'offline';
  setNetworkStatus: (status: 'online' | 'offline') => void;
}

export const useGlobalState = create<GlobalState>((set) => ({
  // App lifecycle
  isAppReady: false,
  setAppReady: (status) => set({ isAppReady: status }),

  // Global loading
  isGlobalLoading: false,
  setGlobalLoading: (status) => set({ isGlobalLoading: status }),

  // Error
  globalError: null,
  setGlobalError: (error) => set({ globalError: error }),

  // UI layout
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

  // Session & version
  sessionId: crypto.randomUUID(),
  appVersion: 'v24',

  // Network status
  networkStatus: 'online',
  setNetworkStatus: (status) => set({ networkStatus: status }),
}));
