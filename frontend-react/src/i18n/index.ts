import en from "./en.json";
import zh from "./zh.json";

// 自动从 JSON 中提取所有 key
export type TranslationKey = keyof typeof en;

// 语言类型
export type Lang = "en" | "zh";

// 翻译表类型
export const translations: Record<Lang, Record<TranslationKey, string>> = {
  en,
  zh,
};

// t() 函数：完全类型安全
export function t(key: TranslationKey, lang: Lang = "zh"): string {
  return translations[lang][key];
}
