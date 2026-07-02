import { create } from 'zustand';
import zhTexts from '../i18n/zh.json';
import enTexts from '../i18n/en.json';

type Language = 'zh' | 'en';

interface LanguageState {
  current: Language;
  texts: Record<string, any>;
  setLanguage: (lang: Language) => void;
}

export const useLanguageState = create<LanguageState>((set) => ({
  current: 'zh',
  texts: {
    zh: zhTexts,
    en: enTexts,
  },
  setLanguage: (lang) => set({ current: lang }),
}));
