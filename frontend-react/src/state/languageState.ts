import { create } from "zustand";
import type { Lang } from "../i18n";

interface LanguageState {
  language: Lang;
  setLanguage: (lang: Lang) => void;
}

export const useLanguageStore = create<LanguageState>((set) => ({
  language: "zh",
  setLanguage: (lang: Lang) => set({ language: lang })
}));
