import { create } from 'zustand';
import lightTheme from '../theme/lightTheme';
import darkTheme from '../theme/darkTheme';

type ThemeMode = 'light' | 'dark';

interface ThemeState {
  current: ThemeMode;
  theme: Record<string, any>;
  toggleTheme: () => void;
  setTheme: (mode: ThemeMode) => void;
}

export const useThemeState = create<ThemeState>((set) => ({
  current: 'dark',
  theme: darkTheme,

  toggleTheme: () =>
    set((state) => {
      const newMode = state.current === 'dark' ? 'light' : 'dark';
      return {
        current: newMode,
        theme: newMode === 'dark' ? darkTheme : lightTheme,
      };
    }),

  setTheme: (mode) =>
    set({
      current: mode,
      theme: mode === 'dark' ? darkTheme : lightTheme,
    }),
}));
