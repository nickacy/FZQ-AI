import en from "./en.json";
import zh from "./zh.json";

export type TranslationKey = keyof typeof en;
export type Lang = "en" | "zh";

export const translations: Record<Lang, Record<TranslationKey, string>> = {
  en,
  zh,
};

export function t(key: TranslationKey, lang: Lang = "zh"): string {
  return translations[lang][key];
}
